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

# Diccionario de traducciones
TRANSLATIONS = {
    "damagedVehicle": "Vehículo Averiado",
    "roadClosed": "Corte Total",
    "restrictions": "Restricciones",
    "narrowLanes": "Carriles Estrechos"
}

# Función para comprobar si un valor es válido
def is_valid(value):
    return value is not None and value.strip()

# Función para formatear fecha y hora
def format_datetime(datetime_str):
    try:
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime("%d/%m/%Y - %H:%M:%S")
    except ValueError:
        return datetime_str

# Función para traducir términos
def translate(value):
    return TRANSLATIONS.get(value, value)

# Función para procesar un archivo XML y extraer información detallada
def process_all_regions():
    all_incidents = []

    for region_name, url in REGIONS.items():
        try:
            # Descargar el archivo XML
            response = requests.get(url)
            response.raise_for_status()

            # Parsear el contenido XML
            root = ET.fromstring(response.content)

            # Procesar los incidentes
            for situation in root.findall(".//_0:situation", NS):
                properties = {}
                geometry = {}

                # Extraer información principal
                situation_id = situation.get("id")
                situation_record = situation.find(".//_0:situationRecord", NS)
                creation_time = situation_record.find(".//_0:situationRecordCreationTime", NS)
                incident_type = situation_record.find(".//_0:vehicleObstructionType", NS)
                source_info = situation_record.find(".//_0:sourceInformation/_0:sourceName/_0:value", NS)
                location_info = situation_record.find(".//_0:groupOfLocations/_0:locationContainedInGroup", NS)

                # Extraer detalles de ubicación
                latitude = location_info.find(".//_0:latitude", NS)
                longitude = location_info.find(".//_0:longitude", NS)
                road_number = location_info.find(".//_0:referencePoint/_0:roadNumber", NS)
                administrative_area = location_info.find(".//_0:referencePoint/_0:administrativeArea/_0:value", NS)

                # Asignar valores a las propiedades
                if is_valid(situation_id):
                    properties["ID del incidente"] = situation_id
                if creation_time is not None and is_valid(creation_time.text):
                    properties["Fecha de creación"] = format_datetime(creation_time.text)
                if incident_type is not None and is_valid(incident_type.text):
                    properties["Tipo de incidente"] = translate(incident_type.text)  # Traducir tipo de incidente
                if source_info is not None and is_valid(source_info.text):
                    properties["Fuente"] = source_info.text
                if road_number is not None and is_valid(road_number.text):
                    properties["Carretera"] = road_number.text
                if administrative_area is not None and is_valid(administrative_area.text):
                    properties["Área administrativa"] = administrative_area.text

                # Asignar coordenadas
                if latitude is not None and longitude is not None:
                    geometry = {
                        "type": "Point",
                        "coordinates": [float(longitude.text), float(latitude.text)]
                    }

                # Agregar datos al conjunto si tienen propiedades válidas
                if properties and geometry:
                    all_incidents.append({
                        "type": "Feature",
                        "properties": properties,
                        "geometry": geometry
                    })

        except Exception as e:
            print(f"Error procesando la región {region_name}: {e}")

    # Crear el archivo GeoJSON combinado
    geojson_data = {
        "type": "FeatureCollection",
        "features": all_incidents
    }
    with open("traffic_data.geojson", "w") as f:
        json.dump(geojson_data, f, indent=2, ensure_ascii=False)

    print("Archivo GeoJSON generado con éxito.")

# Ejecutar la función
process_all_regions()
