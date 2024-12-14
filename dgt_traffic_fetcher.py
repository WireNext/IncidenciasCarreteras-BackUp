import requests
import os
from xml.etree import ElementTree
import json

# URLs de las regiones (personaliza estas con las que necesites)
DGT_REGIONS = {
    "Resto españa": "https://infocar.dgt.es/etraffic/IncidenciasRegion1.xml",
    "Cataluña": "http://infocar.dgt.es/datex2/sct/SituationPublication/all/content.xml",
    "Pais Vasco": "http://infocar.dgt.es/datex2/dt-gv/SituationPublication/all/content.xml",
}

# Ruta de salida
OUTPUT_FILE = "datos_trafico.json"

def procesar_xml_a_dict(xml_content):
    """Convierte el contenido XML en un diccionario legible"""
    root = ElementTree.fromstring(xml_content)
    datos = []

    for incidencia in root.findall(".//incidencia"):
        datos.append({
            "id": incidencia.find("id").text if incidencia.find("id") is not None else None,
            "tipo": incidencia.find("tipo").text if incidencia.find("tipo") is not None else None,
            "descripcion": incidencia.find("descripcion").text if incidencia.find("descripcion") is not None else None,
            "localizacion": incidencia.find("localizacion").text if incidencia.find("localizacion") is not None else None,
            "fecha": incidencia.find("fecha").text if incidencia.find("fecha") is not None else None,
        })

    return datos

def obtener_datos_de_regiones():
    """Obtiene y procesa los datos XML de todas las regiones."""
    datos_combinados = {}

    for region, url in DGT_REGIONS.items():
        try:
            respuesta = requests.get(url)
            respuesta.raise_for_status()

            # Procesar el XML y convertirlo a un formato estructurado
            datos_region = procesar_xml_a_dict(respuesta.content)
            datos_combinados[region] = datos_region
            print(f"Datos de {region} descargados y procesados correctamente.")

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de {region}: {e}")
        except ElementTree.ParseError as e:
            print(f"Error al procesar el XML de {region}: {e}")

    return datos_combinados

def guardar_datos_en_json(datos):
    """Guarda los datos combinados en un archivo JSON."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)
    print(f"Datos guardados en {OUTPUT_FILE}.")

if __name__ == "__main__":
    # Obtener datos y guardarlos
    datos = obtener_datos_de_regiones()
    guardar_datos_en_json(datos)
