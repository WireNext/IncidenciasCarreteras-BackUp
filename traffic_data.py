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

# Definir el espacio de nombres para el XML
NS = {'_0': 'http://datex2.eu/schema/1_0/1_0'}

# Función para procesar un archivo XML desde una URL y extraer los datos necesarios
def process_xml_from_url(url, region_name):
    try:
        # Descargar el archivo XML desde la URL
        response = requests.get(url)
        response.raise_for_status()  # Verifica errores HTTP

        # Parsear el contenido XML
        root = ET.fromstring(response.content)

        # Procesar los incidentes en el archivo XML
        incident_count = 0
        for location_group in root.findall(".//_0:groupOfLocations/_0:locationContainedInGroup", NS):
            # Extraer coordenadas
            latitude = location_group.find(".//_0:pointCoordinates/_0:latitude", NS).text
            longitude = location_group.find(".//_0:pointCoordinates/_0:longitude", NS).text
            location_name = location_group.find(".//_0:name/_0:descriptor/_0:value", NS).text

            # Extraer más detalles: tipo de incidente, carretera, hora, etc.
            description = location_group.find(".//_0:situationRecord/_0:impact/_0:impactDetails/_0:trafficRestrictionType", NS)
            description = description.text if description is not None else "Desconocido"

            # Obtener información sobre la carretera
            road = location_group.find(".//_0:situationRecord/_0:situationRecordCreationReference", NS)
            road = road.text if road is not None else "Desconocida"

            # Fecha y hora (si está disponible)
            time = location_group.find(".//_0:situationRecord/_0:situationRecordCreationTime", NS)
            time = time.text if time is not None else "Desconocido"

            # Depuración: verificar qué datos se están extrayendo
            print(f"Extrayendo incidente: {location_name}, {latitude}, {longitude}, {description}, {road}, {time}")

            # Verificar que las coordenadas sean válidas antes de agregarlas
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (ValueError, TypeError):
                print(f"Coordenadas inválidas para incidente en {location_name}. Saltando este incidente.")
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
                    "description": f"{description} en {road} ({location_name})",
                    "road": road,
                    "time": time,
                    "incident_type": description
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
