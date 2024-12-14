import xml.etree.ElementTree as ET

# Función para verificar si un valor no está vacío
def is_valid(value):
    return value is not None and value.text.strip() != ""

# Función para realizar las sustituciones de palabras en incidentType
def translate_incident_type(incident_type):
    translations = {
        "flooding": "Inundación",
        "roadClosed": "Corte Total",
        "restrictions": "Restricciones",
        "narrowLanes": "Carriles Estrechos"
    }
    return translations.get(incident_type.lower(), incident_type)  # Retorna la traducción o el valor original

# Leer el archivo XML de ejemplo
tree = ET.parse('archivo.xml')  # Cambia 'archivo.xml' por la ruta correcta de tu archivo
root = tree.getroot()

# Recorrer todos los elementos del XML para extraer los datos
features = []

for situation in root.findall('.//_0:situation', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"}):
    properties = {}

    # Obtener la fecha de creación
    situation_creation_time = situation.find('.//_0:situationRecordCreationTime', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"})
    if is_valid(situation_creation_time):
        properties["fecha"] = situation_creation_time.text  # Asignar la fecha

    # Obtener el motivo (en este caso el tipo de obstrucción ambiental)
    environmental_obstruction_type = situation.find('.//_0:environmentalObstructionType', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"})
    if is_valid(environmental_obstruction_type):
        obstruction_type_value = environmental_obstruction_type.text.lower()  # Convertir a minúsculas para asegurar coincidencias
        # Traducir el tipo de incidente
        if obstruction_type_value == 'flooding':
            properties["motivo"] = "Inundación"
        else:
            properties["incidentType"] = translate_incident_type(obstruction_type_value)

    # Obtener la carretera y el punto kilométrico
    road_number = situation.find('.//_0:roadNumber', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"})
    if is_valid(road_number):
        properties["carretera"] = road_number.text  # Campo carretera

    reference_point_distance = situation.find('.//_0:referencePointDistance', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"})
    if is_valid(reference_point_distance):
        properties["kilometro"] = reference_point_distance.text  # Campo punto kilométrico

    # Obtener la dirección
    direction_relative = situation.find('.//_0:directionRelative', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"})
    if is_valid(direction_relative):
        if direction_relative.text.lower() == 'positive':
            properties["direction"] = "Creciente"
        elif direction_relative.text.lower() == 'negative':
            properties["direction"] = "Decreciente"

    # Obtener las coordenadas
    location = situation.find('.//_0:groupOfLocations//_0:locationContainedInGroup//_0:tpeglinearLocation//_0:to//_0:pointCoordinates', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"})
    if location is not None:
        latitude = location.find('.//_0:latitude', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"})
        longitude = location.find('.//_0:longitude', namespaces={"_0": "http://datex2.eu/schema/1_0/1_0"})
        if is_valid(latitude) and is_valid(longitude):
            # Crear un objeto de tipo GeoJSON
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(longitude.text), float(latitude.text)]
                },
                "properties": properties
            }
            features.append(feature)

# Crear el GeoJSON final
geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Para guardar el GeoJSON en un archivo
import json
with open('traffic_data.geojson', 'w') as geojson_file:
    json.dump(geojson, geojson_file, indent=4)
