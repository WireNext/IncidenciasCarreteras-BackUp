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
    "roadClosed": "Corte Total",
    "restrictions": "Restricciones",
    "narrowLanes": "Carriles Estrechos"
}
# Función para comprobar si un valor es válido (no es nulo, "Desconocido", ni vacío)
def is_valid(value):
    return value is not None and value.strip() and value.lower() != "desconocido"
@@ -54,28 +61,30 @@

            # Traducir el tipo de incidente si está presente
            if environmental_obstruction_type is not None and is_valid(environmental_obstruction_type.text):
                properties["incident_type"] = translate_incident_type(environmental_obstruction_type.text)
                original_type = environmental_obstruction_type.text
                translated_type = TRANSLATIONS.get(original_type, original_type)  # Buscar traducción, usar original si no hay
                properties["incident_type"] = translated_type

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
        file_name = f"{region_name.replace(' ', '_')}_traffic_data.geojson"
        with open(file_name, "w") as f:
            json.dump(geojson_data, f, indent=2)

        print(f"Archivo GeoJSON generado con éxito para {region_name}")

    except Exception as e:
        print(f"Error procesando {region_name} desde {url}: {e}")
