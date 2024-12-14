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
        # Convertir la fecha y hora de ISO 8601 a un formato más amigable
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime("%d/%m/%Y - %H:%M:%S")
    except ValueError:
        return datetime_str  # Si no se puede convertir, devolver el valor original

# Función para traducir los tipos de incidentes
def translate_incident_type(incident_type):
    translations = {
        "flooding": "Inundación",
        "roadClosed": "Corte Total",
        "restrictions": "Restricciones",
        "narrowLanes": "Carriles Estrechos"
    }
    return translations.get(incident_type.lower(), incident_type)  # Retorna la traducción o el valor original

# Función para procesar un archivo XML desde una URL y extraer los datos necesarios
def process_xml_from_url(url, region_name):
    try:
        # Descargar el archivo XML desde la URL
        response = requests.get(url)
        response.raise_for_status()  # Verifica errores HTTP

        # Parsear el contenido XML
        root = ET.fromstring(response.content)

        # Lista para almacenar los incidentes procesados
        incidents = []

        # Procesar los incidentes en el archivo XML
        for situation in root.findall(".//_0:situation", NS):
            # Extraer los datos relevantes
            situation_creation_time = situation.find(".//_0:situationRecordCreationTime", NS)
            environmental_obstruction_type = situation.find(".//_0:environmentalObstructionType", NS)

            # Asignar valores a las propiedades si están presentes y son válidas
            properties = {}

            # Formatear la fecha y hora si está presente
            if situation_creation_time is not None and is_valid(situation_creation_time.text):
                properties["creation_time"] = format_datetime(situation_creation_time.text)

            # Traducir el tipo de incidente si está presente
            if environmental_obstruction_type is not None and is_valid(environmental_obstruction_type.text):
                properties["incident_type"] = translate_incident_type(environmental_obstruction_type.text)

            # Crear el objeto del incidente
            if properties:
                incidents.append({
                    "type": "Feature",
                    "properties": properties,
                    "geometry": None  # Asigna una geometría si es necesario
                })

        # Crear el archivo GeoJSON
        geojson_data = {
            "type": "FeatureCollection",
            "features": incidents
        }

        # Guardar el archivo GeoJSON
        with open("traffic_data.geojson", "w") as f:
            json.dump(geojson_data, f, indent=2)

        print(f"Archivo GeoJSON generado con éxito para {region_name}")

    except Exception as e:
        print(f"Error procesando {region_name} desde {url}: {e}")

# Procesar todos los archivos XML de las regiones especificadas
for region_name, url in REGIONS.items():
    print(f"\nProcesando región: {region_name} desde {url}")
    process_xml_from_url(url, region_name)
