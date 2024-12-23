import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd

class AutoescuelaScraper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def get_autoescuela_details(self, autoescuela_element):
        """Extrae detalles de una autoescuela específica"""
        details = {}
        try:
            # Click en la autoescuela
            autoescuela_element.click()
            time.sleep(2)
            
            # Extraer información básica
            details['nombre'] = self.safe_get_text('.fontHeadlineSmall')
            details['valoracion'] = self.safe_get_attribute('span[role="img"]', 'aria-label')
            details['num_resenas'] = self.safe_get_text('button[aria-label*="reseñas"]')
            details['direccion'] = self.safe_get_text('button[data-item-id*="address"]')
            details['telefono'] = self.safe_get_text('button[data-item-id*="phone"]')
            details['web'] = self.safe_get_attribute('a[data-item-id*="website"]', 'href')
            
            # Extraer horarios
            details['horarios'] = self.get_horarios()
            
            # Extraer URLs de imágenes
            details['imagenes'] = self.get_image_urls()
            
            return details
        except Exception as e:
            print(f"Error al extraer detalles: {e}")
            return None

    def safe_get_text(self, selector):
        """Obtiene texto de manera segura"""
        try:
            element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return element.text
        except:
            return None

    def safe_get_attribute(self, selector, attribute):
        """Obtiene atributo de manera segura"""
        try:
            element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return element.get_attribute(attribute)
        except:
            return None

    def get_horarios(self):
        """Extrae los horarios"""
        try:
            horarios = {}
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
            for row in rows:
                dia = row.find_element(By.CSS_SELECTOR, 'th').text
                horario = row.find_element(By.CSS_SELECTOR, 'td').text
                horarios[dia] = horario
            return horarios
        except:
            return {}

    def get_image_urls(self):
        """Extrae URLs de imágenes"""
        try:
            images = self.driver.find_elements(By.CSS_SELECTOR, 'img[src*="googleusercontent"]')
            return [img.get_attribute('src') for img in images]
        except:
            return []

    def scrape_autoescuelas(self, limit=15):
        """Scraping principal de autoescuelas"""
        self.driver.get('https://www.google.com/maps/search/autoescuelas+barcelona')
        time.sleep(3)
        
        results = []
        autoescuelas = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')[:limit]
        
        for autoescuela in autoescuelas:
            details = self.get_autoescuela_details(autoescuela)
            if details:
                results.append(details)
                
        return results

class GoogleSheetsUpdater:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        self.creds = self.get_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)

    def get_credentials(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def update_sheet(self, data, spreadsheet_id, range_name):
        """Actualiza Google Sheet con los datos"""
        try:
            df = pd.DataFrame(data)
            values = [df.columns.values.tolist()] + df.values.tolist()
            body = {
                'values': values
            }
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            print(f"Sheet actualizada exitosamente: {datetime.now()}")
        except Exception as e:
            print(f"Error actualizando sheet: {e}")

def main():
    load_dotenv()
    
    # Iniciar scraping
    scraper = AutoescuelaScraper()
    results = scraper.scrape_autoescuelas()
    scraper.driver.quit()
    
    # Actualizar Google Sheet
    if results:
        updater = GoogleSheetsUpdater()
        spreadsheet_id = os.getenv('GOOGLE_SHEET_ID')
        updater.update_sheet(results, spreadsheet_id, 'A1')

if __name__ == "__main__":
    main()
