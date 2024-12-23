# Autoescuelas Barcelona Scraper

Scraper automático para obtener información detallada de autoescuelas en Barcelona y actualizar un Google Sheet.

## Características

- Scraping automático cada 20 minutos
- Extracción de información detallada:
  - Nombre
  - Valoración y número de reseñas
  - Dirección
  - Teléfono
  - Sitio web
  - Horarios
  - URLs de imágenes
- Actualización automática de Google Sheets
- Ejecución mediante GitHub Actions

## Configuración

1. Crear un proyecto en Google Cloud Console
2. Habilitar Google Sheets API
3. Crear credenciales (OAuth 2.0)
4. Crear un Google Sheet y obtener su ID
5. Configurar los siguientes secrets en GitHub:
   - GOOGLE_CREDENTIALS: Contenido del archivo credentials.json
   - GOOGLE_TOKEN: Token de acceso generado
   - GOOGLE_SHEET_ID: ID del Google Sheet

## Uso

El scraper se ejecuta automáticamente cada 20 minutos mediante GitHub Actions. También puede ejecutarse manualmente desde la pestaña Actions del repositorio.

## Desarrollo local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar scraper
python scraper.py
```

## Estructura del proyecto

```
├── .github/
│   └── workflows/
│       └── scrape.yml    # Configuración de GitHub Actions
├── scraper.py           # Script principal
├── requirements.txt     # Dependencias
└── README.md
```