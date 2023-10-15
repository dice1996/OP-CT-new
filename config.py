# Flask configurations
SECRET_KEY = 'asdf5s64gdf/gdf5h14fgh/f6g3jghj45dfg3d'
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 1234

# Excel data source
EXCEL_URL = 'https://drive.google.com/uc?export=download&id=1pafSi4jvFrLr_LZLI1LBhVxCLfbY...'

# Static file path pattern
STATIC_FILE_PATH_PATTERN = './static/upload/orders/{city}/{year}/{month}/{day}/{order_number}.pdf'

# NocoDB configurations
NOCO_DB_URL = 'https://db.ceky.me/api/v1/db/data/v1/'
API_TOKEN = 'jpgFE3jk3pN9R4S52be05kEG9D-EQbBjiFNrig4x'
HEADERS = {
    'xc-auth': API_TOKEN,
    'xc-token': API_TOKEN,
    'Content-Type': 'application/json',
    'X-Api-Version': '1.0.0'
}