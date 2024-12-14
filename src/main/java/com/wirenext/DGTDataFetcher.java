package com.wirenext; // El paquete debe estar al principio

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;
import javax.xml.parsers.*;
import org.w3c.dom.*;
import com.fasterxml.jackson.databind.ObjectMapper;

public class DGTDataFetcher {

    // Lista de URLs de la DGT
    private static final List<String> DGT_API_URLS = Arrays.asList(
        "https://nap.dgt.es/dataset/incidencias-dgt", // Excepto Pais Vasco y Cataluña
        "https://nap.dgt.es/dataset/incidencias-dt-gv", // Pais Vasco
        "https://nap.dgt.es/dataset/incidencias-sct"  // Cataluña
    );

    // Ruta de salida del archivo GeoJSON
    private static final String OUTPUT_FILE = "target/incidencias.geojson";

    public static void main(String[] args) {
        try {
            List<Map<String, Object>> allFeatures = new ArrayList<>();

            // Iterar sobre cada URL para obtener datos
            for (String apiUrl : DGT_API_URLS) {
                System.out.println("Obteniendo datos de: " + apiUrl);
                List<Map<String, Object>> features = fetchDataFromUrl(apiUrl);
                allFeatures.addAll(features);
            }

            // Generar archivo GeoJSON combinando todos los datos
            generateGeoJSON(allFeatures);
            System.out.println("Archivo GeoJSON generado correctamente: " + OUTPUT_FILE);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Método para obtener datos de una URL
    private static List<Map<String, Object>> fetchDataFromUrl(String apiUrl) throws Exception {
        List<Map<String, Object>> features = new ArrayList<>();

        // Conexión HTTP
        URL url = new URL(apiUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        
        if (conn.getResponseCode() == 200) {
            InputStream inputStream = conn.getInputStream();
            
            // Convertir XML a objetos (si los datos son XML en formato DATEX II)
            features = parseDATEX2ToGeoJSON(inputStream);
            
            inputStream.close();
        } else {
            System.out.println("Error al obtener datos de " + apiUrl + ": " + conn.getResponseCode());
        }
        return features;
    }

    // Método de ejemplo: convierte XML DATEX II a estructura GeoJSON
    private static List<Map<String, Object>> parseDATEX2ToGeoJSON(InputStream xmlStream) throws Exception {
        List<Map<String, Object>> features = new ArrayList<>();
        
        // Crear el parser XML
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(xmlStream);
        doc.getDocumentElement().normalize();

        // Ejemplo: Extraer datos simples del XML (adaptar a DATEX II real)
        NodeList incidentNodes = doc.getElementsByTagName("incident");
        for (int i = 0; i < incidentNodes.getLength(); i++) {
            Node node = incidentNodes.item(i);
            if (node.getNodeType() == Node.ELEMENT_NODE) {
                Element element = (Element) node;

                // Crear una estructura GeoJSON Feature
                Map<String, Object> feature = new HashMap<>();
                feature.put("type", "Feature");
                
                Map<String, Double> geometry = new HashMap<>();
                geometry.put("lat", Double.parseDouble(element.getElementsByTagName("latitude").item(0).getTextContent()));
                geometry.put("lon", Double.parseDouble(element.getElementsByTagName("longitude").item(0).getTextContent()));
                feature.put("geometry", geometry);

                Map<String, String> properties = new HashMap<>();
                properties.put("description", element.getElementsByTagName("description").item(0).getTextContent());
                feature.put("properties", properties);

                features.add(feature);
            }
        }
        return features;
    }

    // Generar el archivo GeoJSON con los datos combinados
    private static void generateGeoJSON(List<Map<String, Object>> features) throws IOException {
        Map<String, Object> geoJSON = new HashMap<>();
        geoJSON.put("type", "FeatureCollection");
        geoJSON.put("features", features);

        // Convertir el mapa a JSON y escribirlo a un archivo
        ObjectMapper mapper = new ObjectMapper();
        mapper.writeValue(new File(OUTPUT_FILE), geoJSON);
    }
}
