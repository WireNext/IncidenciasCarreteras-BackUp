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

# Procesar XML y combinar todos los datos en un único GeoJSON
def process_all_regions():
    all_incidents = []

    for region_name, url in REGIONS.items():
        try:
            # Descargar el archivo XML
            response = requests.get(url)
            response.raise_for_status()

            # Parsear el contenido XML
            root = ET.fromstring(response.content)

            # Procesar incidentes
            for situation in root.findall(".//_0:situation", NS):
                properties = {}
                geometry = {}

                situation_creation_time = situation.find(".//_0:situationRecordCreationTime", NS)
                environmental_obstruction_type = situation.find(".//_0:environmentalObstructionType", NS)
                longitude = situation.find(".//_0:longitude", NS)
                latitude = situation.find(".//_0:latitude", NS)

                # Formatear la fecha y traducir tipo de incidente
                if situation_creation_time is not None and is_valid(situation_creation_time.text):
                    properties["Fecha de Creación"] = format_datetime(situation_creation_time.text)
                if environmental_obstruction_type is not None and is_valid(environmental_obstruction_type.text):
                    properties["Tipo de Incidente"] = translate_incident_type(environmental_obstruction_type.text)

                # Añadir coordenadas si existen
                if longitude is not None and latitude is not None and is_valid(longitude.text) and is_valid(latitude.text):
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
            print(f"Error procesando {region_name}: {e}")

    # Crear el archivo GeoJSON combinado
    geojson_data = {
        "type": "FeatureCollection",
        "features": all_incidents
    }
    with open("traffic_data.geojson", "w") as f:
        json.dump(geojson_data, f, indent=2)

    print("Archivo GeoJSON combinado generado con éxito.")

# Ejecutar la función
process_all_regions()
