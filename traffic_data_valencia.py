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

    # Procesar cada 'Feature' en el GeoJSON
    for feature in data['features']:
        # Agregar un estilo personalizado para cada punto (por ejemplo, color dependiendo del estado de tráfico)
        # Aquí supongo que hay un campo 'estado' que puede definir el color del punto.
        # Puedes adaptarlo según los campos reales que tengas en la respuesta de la API.

        estado = feature['properties'].get('estado', 'desconocido')

        # Definir color en función del estado del tráfico (esto es solo un ejemplo, modifica según tus necesidades)
        if estado == 'Valido_p':
            color = 'green'
        elif estado == 'Valido_p':
            color = 'red'
        else:
            color = 'yellow'

        # Definir el estilo en cada 'Feature'
        feature['properties']['style'] = {
            'color': color,  # Color del marcador
            'weight': 5,     # Grosor del borde del marcador
            'opacity': 0.7,  # Opacidad
            'fillColor': color,  # Color de relleno (si es un círculo)
            'fillOpacity': 0.5  # Opacidad del relleno
        }

    # Guardar los datos con estilo en un archivo GeoJSON
    with open('valencia_trafico_estilizado.geojson', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Archivo GeoJSON de tráfico de Valencia con estilo guardado con éxito.")
else:
    print(f"Error al obtener los datos: {response.status_code}")
