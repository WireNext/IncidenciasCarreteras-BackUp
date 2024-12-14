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

# Función para comprobar si un valor es válido (no es nulo ni "Desconocido")
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

# Función para realizar las sustituciones de palabras
def translate_incident_type(incident_type):
    # Realizar las sustituciones
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
            network_management_type = situation.find(".//_0:networkManagementType", NS)
            direction_relative = situation.find(".//_0:directionRelative", NS)
            road_number = situation.find(".//_0:roadNumber", NS)
            reference_point_distance = situation.find(".//_0:referencePointDistance", NS)

            # Extraer las coordenadas de cada incidente
            coordinates = situation.findall(".//_0:pointCoordinates", NS)
            latitude = None
            longitude = None

            for coord in coordinates:
                lat = coord.find(".//_0:latitude", NS)
                lon = coord.find(".//_0:longitude", NS)

                # Si las coordenadas están presentes y son válidas, asignar
                if lat is not None and lon is not None and is_valid(lat.text) and is_valid(lon.text):
                    latitude = lat.text
                    longitude = lon.text
                    break  # Usamos la primera coordenada válida encontrada

            # Asignar valores a las propiedades si están presentes y son válidas
            properties = {}

            # Formatear la fecha y hora si está presente
            if situation_creation_time is not None and is_valid(situation_creation_time.text):
                formatted_time = format_datetime(situation_creation_time.text)
                properties["creation_time"] = formatted_time

            # Asignar el tipo de incidente y traducirlo si es necesario
            if environmental_obstruction_type is not None and is_valid(environmental_obstruction_type.text):
                translated_type = translate_incident_type(environmental_obstruction_type.text)
                properties["incident_type"] = translated_type

            # Asignar el estado de la carretera si está presente
            if network_management_type is not None and is_valid(network_management_type.text):
                properties["network_status"] = network_management_type.text

            # Asignar la dirección según 'positive' o 'negative'
            if direction_relative is not None and is_valid(direction_relative.text):
                if direction_relative.text.lower() == 'positive':
                    properties["direction"] = "Creciente"
                elif direction_relative.text.lower() == 'negative':
                    properties["direction"] = "Decreciente"

            # Asignar la carretera y el punto kilométrico si están presentes
            if road_number is not None and is_valid(road_number.text):
                properties["road"] = road_number.text

            if reference_point_distance is not None and is_valid(reference_point_distance.text):
                properties["kilometer_point"] = reference_point_distance.text

            # Si hay coordenadas válidas, agregar la geometría
            if latitude is not None and longitude is not None:
                geometry = {
                    "type": "Point",
                    "coordinates": [float(longitude), float(latitude)]  # Longitud, Latitud
                }

                # Crear el campo de descripción personalizado
                description = ""
                if 'incident_type' in properties:
                    description += f"<b>Motivo:</b> {properties['incident_type']}<br>"
                if 'creation_time' in properties:
                    description += f"<b>Fecha de Creación:</b> {properties['creation_time']}<br>"
                if 'network_status' in properties:
                    description += f"<b>Estado de la Carretera:</b> {properties['network_status']}<br>"
                if 'direction' in properties:
                    description += f"<b>Dirección:</b> {properties['direction']}<br>"
                if 'road' in properties:
                    description += f"<b>Carretera:</b> {properties['road']}<br>"
                if 'kilometer_point' in properties:
                    description += f"<b>Punto Kilométrico:</b> {properties['kilometer_point']}<br>"

                # Crear el objeto del incidente con la descripción incluida
                incident = {
                    "type": "Feature",
                    "properties": {
                        "description": description
                    },
                    "geometry": geometry
                }
                incidents.append(incident)
                # Solo agregamos al incidente si la descripción no está vacía
                if description.strip():
                    incident = {
                        "type": "Feature",
                        "properties": {
                            "description": description
                        },
                        "geometry": geometry
                    }
                    incidents.append(incident)

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
