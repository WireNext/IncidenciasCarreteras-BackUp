import xml.etree.ElementTree as ET
import json
import requests

# Lista de regiones con sus respectivas URLs de archivos XML
REGIONS = {
    "Cataluña": "http://infocar.dgt.es/datex2/sct/SituationPublication/all/content.xml",
    "País Vasco": "http://infocar.dgt.es/datex2/dt-gv/SituationPublication/all/content.xml",
    "Resto España": "http://infocar.dgt.es/datex2/dgt/SituationPublication/all/content.xml"
}

# Mantener el nombre del archivo sin cambios
OUTPUT_FILE = "traffic_data.geojson"

# Estructura inicial del GeoJSON
data = {
    "type": "FeatureCollection",
    "features": []
}

# Función para procesar un archivo XML desde una URL y extraer los datos necesarios
def process_xml_from_url(url, region_name):
    try:
        # Descargar el archivo XML desde la URL
        response = requests.get(url)
        response.raise_for_status()  # Verifica errores HTTP

        # Parsear el contenido XML
        root = ET.fromstring(response.content)

        # Depuración: imprimir el XML para verificar su estructura
        # print(ET.tostring(root, encoding='utf8').decode('utf8'))

        # Procesar los incidentes en el archivo XML
        incident_count = 0
        for incident in root.findall(".//incident"):
            # Extraer datos necesarios; ajusta las etiquetas según el XML
            latitude = incident.find("latitude").text
            longitude = incident.find("longitude").text
            description = incident.find("description").text
            road = incident.find("road").text

            # Depuración: verificar qué datos se están extrayendo
            print(f"Extrayendo incidente: {description}, {road}, {latitude}, {longitude}")

            # Verificar que las coordenadas sean válidas antes de agregarlas
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (ValueError, TypeError):
                print(f"Coordenadas inválidas para incidente en {road}. Saltando este incidente.")
                continue

            # Crear una Feature para el GeoJSON
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "properties": {
                    "region": region_name,
                    "description": description,
                    "road": road
                }
            }

            # Añadir al GeoJSON
            data["features"].append(feature)
            incident_count += 1

        # Comprobar si se han procesado incidentes
        if incident_count == 0:
            print(f"No se encontraron incidentes en el XML de {region_name}.")
        else:
            print(f"Se procesaron {incident_count} incidentes en {region_name}.")

    except Exception as e:
        print(f"Error procesando {region_name} desde {url}: {e}")

# Procesar todos los archivos XML de las regiones especificadas
for region_name, url in REGIONS.items():
    print(f"Procesando región: {region_name} desde {url}")
    process_xml_from_url(url, region_name)

# Verificar si hay incidentes antes de guardar el archivo
if len(data["features"]) == 0:
    print("No se encontraron incidentes para agregar al GeoJSON.")
else:
    # Guardar el resultado en un archivo GeoJSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as geojson_file:
        json.dump(data, geojson_file, ensure_ascii=False, indent=4)

    print(f"Archivo GeoJSON generado: {OUTPUT_FILE}")
