import xml.etree.ElementTree as ET
import requests
import json

# Lista de regiones con sus respectivas URLs de archivos XML
REGIONS = {
    "Cataluña": "http://infocar.dgt.es/datex2/sct/SituationPublication/all/content.xml",
    "País Vasco": "http://infocar.dgt.es/datex2/dt-gv/SituationPublication/all/content.xml",
    "Resto España": "http://infocar.dgt.es/datex2/dgt/SituationPublication/all/content.xml"
}

# Definir el espacio de nombres para el XML
NS = {'_0': 'http://datex2.eu/schema/1_0/1_0'}

# Función para comprobar si un valor es válido (no es nulo ni "Desconocido")
def is_valid(value):
    return value is not None and value.strip() and value.lower() != "desconocido"

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

            # Extraer las coordenadas si están presentes
            latitude = situation.find(".//_0:pointCoordinates/_0:latitude", NS)
            longitude = situation.find(".//_0:pointCoordinates/_0:longitude", NS)

            # Asignar valores si están presentes y son válidos
            properties = {}

            if situation_creation_time is not None and is_valid(situation_creation_time.text):
                properties["creation_time"] = situation_creation_time.text

            if environmental_obstruction_type is not None and is_valid(environmental_obstruction_type.text):
                properties["incident_type"] = environmental_obstruction_type.text

            if network_management_type is not None and is_valid(network_management_type.text):
                properties["network_status"] = network_management_type.text

            if direction_relative is not None and is_valid(direction_relative.text):
                properties["direction"] = direction_relative.text

            # Si hay coordenadas válidas, agregar la geometría
            if latitude is not None and longitude is not None and is_valid(latitude.text) and is_valid(longitude.text):
                geometry = {
                    "type": "Point",
                    "coordinates": [float(longitude.text), float(latitude.text)]  # Longitud, Latitud
                }

                # Si no hay propiedades válidas, no agregamos este incidente
                if properties:
                    incident = {
                        "type": "Feature",
                        "properties": properties,
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
