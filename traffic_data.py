import xml.etree.ElementTree as ET
import requests
import json
from datetime import datetime

# URLs de las regiones
REGIONS = {
    "Cataluña": "http://infocar.dgt.es/datex2/sct/SituationPublication/all/content.xml",
    "País Vasco": "http://infocar.dgt.es/datex2/dt-gv/SituationPublication/all/content.xml",
    "Resto España": "http://infocar.dgt.es/datex2/dgt/SituationPublication/all/content.xml"
}

# Namespace para XML
NS = {'_0': 'http://datex2.eu/schema/1_0/1_0'}

# Traducción de tipos
TRANSLATIONS = {
    "roadClosed": "Corte Total",
    "restrictions": "Restricciones",
    "narrowLanes": "Carriles Estrechos",
    "damagedVehicle": "Vehículo Averiado",
    "flooding": "Inundación"
}

# Verificar si un valor es válido
def is_valid(value):
    return value is not None and value.strip() and value.lower() != "desconocido"

# Formatear fecha y hora
def format_datetime(datetime_str):
    try:
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime("%d/%m/%Y - %H:%M:%S")
    except ValueError:
        return datetime_str

# Traducir tipos conocidos
def translate_type(value):
    return TRANSLATIONS.get(value, value)

# Procesar un archivo XML desde una URL
def process_xml_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        incidents = []

        for situation in root.findall(".//_0:situation", NS):
            for record in situation.findall(".//_0:situationRecord", NS):
                # Extraer datos principales
                creation_time = record.find(".//_0:situationRecordCreationTime", NS)
                direction = record.find(".//_0:directionRelative", NS)
                road = record.find(".//_0:roadNumber", NS)
                km_point = record.find(".//_0:referencePointDistance", NS)
                latitude = record.find(".//_0:pointCoordinates/_0:latitude", NS)
                longitude = record.find(".//_0:pointCoordinates/_0:longitude", NS)
                vehicle_obstruction = record.find(".//_0:vehicleObstructionType", NS)
                environmental_obstruction = record.find(".//_0:environmentalObstructionType", NS)
                network_management = record.find(".//_0:networkManagementType", NS)

                # Construir descripción
                description = ""
                if is_valid(creation_time.text):
                    description += f"<b>Fecha de Creación:</b> {format_datetime(creation_time.text)}<br>"
                if is_valid(direction.text):
                    description += f"<b>Dirección:</b> {translate_type(direction.text)}<br>"
                if is_valid(road.text):
                    description += f"<b>Carretera:</b> {road.text}<br>"
                if is_valid(km_point.text):
                    description += f"<b>Punto Kilométrico:</b> {km_point.text}<br>"
                if is_valid(vehicle_obstruction.text):
                    description += f"<b>Tipo de Obstáculo:</b> {translate_type(vehicle_obstruction.text)}<br>"
                if is_valid(environmental_obstruction.text):
                    description += f"<b>Obstrucción Ambiental:</b> {translate_type(environmental_obstruction.text)}<br>"
                if is_valid(network_management.text):
                    description += f"<b>Gestión de Red:</b> {translate_type(network_management.text)}<br>"

                # Agregar al GeoJSON si hay coordenadas válidas
                if is_valid(latitude.text) and is_valid(longitude.text):
                    incidents.append({
                        "type": "Feature",
                        "properties": {
                            "description": description
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(longitude.text), float(latitude.text)]
                        }
                    })

        return incidents

    except Exception as e:
        print(f"Error procesando {url}: {e}")
        return []

# Archivo GeoJSON de salida
geojson_file = "traffic_data.geojson"

# Procesar todas las regiones
all_incidents = []
for region_name, url in REGIONS.items():
    print(f"Procesando región: {region_name}")
    all_incidents.extend(process_xml_from_url(url))

# Crear el archivo GeoJSON con todos los datos
geojson_data = {
    "type": "FeatureCollection",
    "features": all_incidents
}

with open(geojson_file, "w") as f:
    json.dump(geojson_data, f, indent=2, ensure_ascii=False)

print(f"Archivo GeoJSON actualizado: {geojson_file}")
