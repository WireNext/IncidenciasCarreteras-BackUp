import xml.etree.ElementTree as ET
import requests
import json
from datetime import datetime

# Lista de regiones con sus respectivas URLs de archivos XML
REGIONS = {
    "Cataluña": "http://infocar.dgt.es/datex2/sct/SituationPublication/all/content.xml",
    "País Vasco": "http://infocar.dgt.es/datex2/dt-gv/SituationPublication/all/content.xml",
    "Resto España": "http://infocar.dgt.es/datex2/dgt/SituationPublication/all/content.xml"
}

# Definir el espacio de nombres para el XML
NS = {'_0': 'http://datex2.eu/schema/1_0/1_0'}

# Función para comprobar si un valor es válido (no es nulo, "Desconocido", ni vacío)
def is_valid(value):
    return value is not None and value.strip() and value.lower() != "desconocido"

# Función para convertir la fecha y hora a un formato más bonito
def format_datetime(datetime_str):
    try:
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime("%d/%m/%Y - %H:%M:%S")
    except ValueError:
        return datetime_str

# Función para traducir tipos de incidentes
def translate_incident_type(incident_type):
    translations = {
        "roadClosed": "Corte Total",
        "restrictions": "Restricciones",
        "narrowLanes": "Carriles Estrechos"
    }
    return translations.get(incident_type.strip(), incident_type)

# Función para procesar un archivo XML desde una URL y extraer los datos necesarios
def process_xml_from_url(url, region_name):
    try:
        response = requests.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        incidents = []

        for situation in root.findall(".//_0:situation", NS):
            # Inicializar description
            description = ""

            # Obtener los datos relevantes del XML
            creation_time = situation.find(".//_0:situationRecordCreationTime", NS)
            incident_type = situation.find(".//_0:environmentalObstructionType", NS)
            road_name = situation.find(".//_0:roadName", NS)
            direction = situation.find(".//_0:directionBound", NS)
            km_point = situation.find(".//_0:affectedLocation/_0:startOfLocation/_0:pointCoordinates/_0:pointCoordinate", NS)
            coordinates = situation.findall(".//_0:pointCoordinates/_0:pointCoordinate", NS)

            # Construir la descripción acumulando datos válidos
            if creation_time is not None and is_valid(creation_time.text):
                description += f"<b>Fecha de Creación:</b> {format_datetime(creation_time.text)}<br>"
            if incident_type is not None and is_valid(incident_type.text):
                description += f"<b>Tipo de Incidente:</b> {translate_incident_type(incident_type.text)}<br>"
            if road_name is not None and is_valid(road_name.text):
                description += f"<b>Carretera:</b> {road_name.text}<br>"
            if direction is not None and is_valid(direction.text):
                description += f"<b>Dirección:</b> {direction.text}<br>"
            if km_point is not None and is_valid(km_point.text):
                description += f"<b>Punto Kilométrico:</b> {km_point.text}<br>"

            # Crear la geometría si las coordenadas están disponibles
            geometry = None
            if coordinates and len(coordinates) == 2:
                try:
                    lng = float(coordinates[0].text)
                    lat = float(coordinates[1].text)
                    geometry = {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    }
                except (TypeError, ValueError):
                    pass

            # Añadir el incidente si tiene datos válidos
            if description and geometry:
                incidents.append({
                    "type": "Feature",
                    "properties": {"description": description},
                    "geometry": geometry
                })

        # Crear y guardar el archivo GeoJSON
        geojson_data = {
            "type": "FeatureCollection",
            "features": incidents
        }

        file_name = "traffic_data.geojson"
        with open(file_name, "w") as f:
            json.dump(geojson_data, f, indent=2)

        print(f"Archivo GeoJSON generado con éxito para {region_name}")

    except Exception as e:
        print(f"Error procesando {region_name} desde {url}: {e}")

# Procesar todos los archivos XML de las regiones especificadas
for region_name, url in REGIONS.items():
    print(f"\nProcesando región: {region_name} desde {url}")
    process_xml_from_url(url, region_name)
