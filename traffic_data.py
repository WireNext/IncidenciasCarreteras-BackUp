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

        # Imprimir todo el XML para verificar la estructura
        print(f"\n--- Estructura XML para {region_name} ---")
        print(ET.tostring(root, encoding='utf-8').decode())

        # Procesar los incidentes en el archivo XML
        incident_count = 0
        for location_group in root.findall(".//_0:groupOfLocations/_0:locationContainedInGroup", NS):
            # Extraer todos los elementos de este grupo de localización para inspección
            print(f"\n--- Detalles del Incidente ---")
            for elem in location_group.iter():
                print(f"Tag: {elem.tag}, Texto: {elem.text}")

            incident_count += 1

        # Comprobar si se han procesado incidentes
        if incident_count == 0:
            print(f"No se encontraron incidentes en el XML de {region_name}.")
        else:
            print(f"Se procesaron {incident_count} incidentes en {region_name}.")

    except Exception as e:
        print(f"Error procesando {region_name} desde {url}: {e}")

# Procesar todos los archivos XML de las regiones especificadas
for region_name, url in REGIONS.items():
    print(f"\nProcesando región: {region_name} desde {url}")
    process_xml_from_url(url, region_name)
