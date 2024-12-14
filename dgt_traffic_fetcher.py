import xml.etree.ElementTree as ET
import json
import os

# Directorio donde se encuentran los archivos XML
XML_DIRECTORY = "xml_files"
OUTPUT_FILE = "traffic_data.geojson"

# Estructura inicial del GeoJSON
data = {
    "type": "FeatureCollection",
    "features": []
}

# Función para procesar un archivo XML y extraer los datos necesarios
def process_xml_file(file_path, region_name):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for incident in root.findall(".//incident"):
            # Extrae datos necesarios, ajusta las etiquetas según el XML
            latitude = incident.find("latitude").text
            longitude = incident.find("longitude").text
            description = incident.find("description").text
            road = incident.find("road").text

            # Crear una Feature para el GeoJSON
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(longitude), float(latitude)]
                },
                "properties": {
                    "region": region_name,
                    "description": description,
                    "road": road
                }
            }

            # Añadir al GeoJSON
            data["features"].append(feature)

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")

# Procesar todos los archivos XML de diferentes regiones
for file_name in os.listdir(XML_DIRECTORY):
    if file_name.endswith(".xml"):
        region_name = os.path.splitext(file_name)[0]  # Asumimos que el nombre del archivo es el de la región
        process_xml_file(os.path.join(XML_DIRECTORY, file_name), region_name)

# Guardar el resultado en un archivo GeoJSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as geojson_file:
    json.dump(data, geojson_file, ensure_ascii=False, indent=4)

print(f"Archivo GeoJSON generado: {OUTPUT_FILE}")
