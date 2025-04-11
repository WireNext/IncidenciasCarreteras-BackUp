import requests
import json

# URL de la API de tráfico de Valencia
url = "https://geoportal.valencia.es/server/rest/services/OPENDATA/Trafico/MapServer/192/query?where=1=1&outFields=*&f=geojson"

# Realizar la solicitud GET para obtener los datos en formato GeoJSON
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Obtener los datos en formato JSON
    data = response.json()

    # Guardar los datos en un archivo GeoJSON
    with open('valencia_trafico.geojson', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Archivo GeoJSON de tráfico de Valencia guardado con éxito.")
else:
    print(f"Error al obtener los datos: {response.status_code}")
