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

# Ruta del archivo GeoJSON existente
OUTPUT_FILE = "traffic_data.geojson"

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

# Leer el archivo GeoJSON existente (si existe)
def load_existing_geojson(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"type": "FeatureCollection", "features": []}  # Crear una estructura vacía si no existe

# Escribir datos al archivo GeoJSON
def save_geojson(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Función para procesar un archivo XML desde una URL y agregar los incidentes al GeoJSON existente
def process_xml_from_url(url, existing_data):
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
                existing_data["features"].append({
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

# Cargar el archivo GeoJSON existente
geojson_data = load_existing_geojson(OUTPUT_FILE)

# Procesar todas las regiones y agregar los incidentes al GeoJSON
for url in REGIONS.values():
    process_xml_from_url(url, geojson_data)

# Guardar el GeoJSON actualizado
save_geojson(OUTPUT_FILE, geojson_data)

print(f"Archivo GeoJSON actualizado con éxito: {OUTPUT_FILE}")
