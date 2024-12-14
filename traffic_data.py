import xml.etree.ElementTree as ET
import requests

# Lista de regiones con sus respectivas URLs de archivos XML
REGIONS = {
    "Cataluña": "http://infocar.dgt.es/datex2/sct/SituationPublication/all/content.xml",
    "País Vasco": "http://infocar.dgt.es/datex2/dt-gv/SituationPublication/all/content.xml",
    "Resto España": "http://infocar.dgt.es/datex2/dgt/SituationPublication/all/content.xml"
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
        for situation in root.findall(".//_0:situation", NS):
            # Extraer los datos relevantes
            situation_creation_time = situation.find(".//_0:situationRecordCreationTime", NS)
            environmental_obstruction_type = situation.find(".//_0:environmentalObstructionType", NS)
            network_management_type = situation.find(".//_0:networkManagementType", NS)
            direction_relative = situation.find(".//_0:directionRelative", NS)

            # Si no se encuentra algún valor, asignar "Desconocido"
            creation_time = situation_creation_time.text if situation_creation_time is not None else "Desconocida"
            obstruction_type = environmental_obstruction_type.text if environmental_obstruction_type is not None else "Desconocido"
            network_status = network_management_type.text if network_management_type is not None else "Desconocido"
            direction = direction_relative.text if direction_relative is not None else "Desconocida"

            # Mostrar la información para cada incidente
            print(f"Incidente: {obstruction_type}")
            print(f"Fecha de Creación: {creation_time}")
            print(f"Estado de la carretera: {network_status}")
            print(f"Dirección: {direction}")
            print("------")

    except Exception as e:
        print(f"Error procesando {region_name} desde {url}: {e}")

# Procesar todos los archivos XML de las regiones especificadas
for region_name, url in REGIONS.items():
    print(f"\nProcesando región: {region_name} desde {url}")
    process_xml_from_url(url, region_name)
