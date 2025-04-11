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
geojson_file = "combined_traffic_data.geojson"  # Nombre del archivo GeoJSON de salida
with open(geojson_file, "w") as f:
    json.dump(geojson_data, f, indent=2, ensure_ascii=False)

print(f"\nArchivo GeoJSON global generado con éxito: {geojson_file}")
