import json

# Cargar los dos archivos GeoJSON
with open('traffic_data.geojson', 'r', encoding='utf-8') as dgt_file:
    dgt_data = json.load(dgt_file)

with open('valencia_trafico.geojson', 'r', encoding='utf-8') as valencia_file:
    valencia_data = json.load(valencia_file)

# Combinar ambos datasets
combined_data = {
    "type": "FeatureCollection",
    "features": dgt_data['features'] + valencia_data['features']
}

# Guardar el archivo combinado
with open('combined_traffic_data.geojson', 'w', encoding='utf-8') as combined_file:
    json.dump(combined_data, combined_file, ensure_ascii=False, indent=2)

print("Archivo GeoJSON combinado guardado con éxito.")
