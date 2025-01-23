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

# Traducción de tipos de incidentes
INCIDENT_TYPE_TRANSLATIONS = {
    "damagedVehicle": "Vehículo Averiado",
    "roadClosed": "Corte Total",
    "restrictions": "Restricciones",
    "narrowLanes": "Carriles Estrechos"
}

# Función para comprobar si un valor es válido
def is_valid(value):
    return value is not None and value.strip() and value.lower() != "desconocido"

# Función para formatear fecha y hora
def format_datetime(datetime_str):
    try:
        dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y - %H:%M:%S")
    except ValueError:
        return datetime_str

# Función para traducir tipo de incidente
def translate_incident_type(incident_type):
    return INCIDENT_TYPE_TRANSLATIONS.get(incident_type, incident_type)

# Lista para almacenar todos los incidentes
all_incidents = []

# Función para procesar un archivo XML desde una URL
def process_xml_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        for situation in root.findall(".//_0:situation", NS):
            situation_creation_time = situation.find(".//_0:situationRecordCreationTime", NS)
            latitude = situation.find(".//_0:latitude", NS)
            longitude = situation.find(".//_0:longitude", NS)
            direction = situation.find(".//_0:tpegDirection", NS)
            road_number = situation.find(".//_0:roadNumber", NS)
            point_km = situation.find(".//_0:referencePointDistance", NS)
            incident_type = situation.find(".//_0:vehicleObstructionType", NS)

            # Construcción de la descripción
            description = ""
            if situation_creation_time is not None and is_valid(situation_creation_time.text):
                description += f"<b>Fecha de Creación:</b> {format_datetime(situation_creation_time.text)}<br>"
            if direction is not None and is_valid(direction.text):
                description += f"<b>Dirección:</b> {direction.text.capitalize()}<br>"
            if road_number is not None and is_valid(road_number.text):
                description += f"<b>Carretera:</b> {road_number.text}<br>"
            if point_km is not None and is_valid(point_km.text):
                description += f"<b>Punto Kilométrico:</b> {float(point_km.text) / 1000:.1f}<br>"
            if incident_type is not None and is_valid(incident_type.text):
                description += f"<b>Tipo de Incidente:</b> {translate_incident_type(incident_type.text)}<br>"

            # Construcción del objeto de incidente
            if latitude is not None and longitude is not None and is_valid(latitude.text) and is_valid(longitude.text):
                all_incidents.append({
                    "type": "Feature",
                    "properties": {
                        "description": description
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            float(longitude.text),
                            float(latitude.text)
                        ]
                    }
                })

    except Exception as e:
        print(f"Error procesando datos desde {url}: {e}")

# Procesar todas las regiones
for url in REGIONS.values():
    process_xml_from_url(url)

# Crear el archivo GeoJSON con todos los incidentes
geojson_data = {
    "type": "FeatureCollection",
    "features": all_incidents
}
output_file = "all_traffic_data.geojson"
with open(output_file, "w") as f:
    json.dump(geojson_data, f, indent=2, ensure_ascii=False)

print(f"Archivo GeoJSON generado con éxito: {output_file}")
