// src/components/MapCanvas.tsx
import React, { useEffect, useRef, useState } from "react";
import "ol/ol.css";
import { Map, View } from "ol";
import { Tile as TileLayer } from "ol/layer";
import { OSM, TileWMS } from "ol/source";
import { fromLonLat } from "ol/proj";
import { defaults as defaultControls, ScaleLine } from "ol/control";
import BaseLayer from "ol/layer/Base";
import axios from "axios";
import { MapCanvasProps } from "../services/types";

const MapCanvas: React.FC<MapCanvasProps> = ({
  selectedLayers,
  onFeatureClick,
  activeBaseLayer,
}) => {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const [mapObject, setMapObject] = useState<Map | null>(null);
  const osmLayerRef = useRef<TileLayer<OSM> | null>(null);
  const dofLayerRef = useRef<TileLayer<TileWMS> | null>(null);

  useEffect(() => {
    if (!mapObject && mapRef.current) {
      // Create base layers
      const osmLayer = new TileLayer({
        source: new OSM(),
        visible: activeBaseLayer === "OSM",
      });
      osmLayer.set("title", "OpenStreetMap");
      osmLayerRef.current = osmLayer;

      const geoserverUrl = process.env.REACT_APP_GEOSERVER_URL || "http://localhost:8080/geoserver";
      
      const dofLayer = new TileLayer({
        source: new TileWMS({
          url: `${geoserverUrl}/wms`,
          params: {
            LAYERS: "croatia:dof_ortho",   // assume this is configured in GeoServer
            FORMAT: "image/png",
            TRANSPARENT: true,
          },
          serverType: "geoserver",
          crossOrigin: "anonymous",
        }),
        visible: activeBaseLayer === "DOF",
      });
      dofLayer.set("title", "Croatia DOF");
      dofLayerRef.current = dofLayer;

      // Create initial map
      const initialMap = new Map({
        target: mapRef.current,
        controls: defaultControls().extend([new ScaleLine()]),
        view: new View({
          center: fromLonLat([16.0, 45.5]), // Rough center of Croatia
          zoom: 7,
          projection: "EPSG:3857",
        }),
        layers: [osmLayer, dofLayer],
      });

      // Click handling for GetFeatureInfo
      initialMap.on("singleclick", async (evt) => {
        const viewResolution = initialMap.getView().getResolution();
        const coordinate = evt.coordinate;
        
        // Build GetFeatureInfo URL for first selected layer
        if (selectedLayers.length > 0 && viewResolution) {
          const layerName = selectedLayers[0];
          const wmsLayers = initialMap.getLayers().getArray().filter(
            (layer: BaseLayer) => layer.get("title") === layerName
          ) as TileLayer<TileWMS>[];

          if (wmsLayers.length > 0) {
            const source = wmsLayers[0].getSource();
            if (source instanceof TileWMS) {
              const url = source.getFeatureInfoUrl(
                coordinate,
                viewResolution,
                "EPSG:3857",
                { 
                  INFO_FORMAT: "application/json", 
                  QUERY_LAYERS: `croatia:${layerName}` 
                }
              );
              if (url) {
                try {
                  const resp = await axios.get(url);
                  if (resp.data && resp.data.features && resp.data.features.length > 0) {
                    onFeatureClick(resp.data.features[0].properties);
                  }
                } catch (error) {
                  console.error("GetFeatureInfo error:", error);
                }
              }
            }
          }
        }
      });

      setMapObject(initialMap);
    }

    // Update base layer visibility
    if (mapObject && osmLayerRef.current && dofLayerRef.current) {
      osmLayerRef.current.setVisible(activeBaseLayer === "OSM");
      dofLayerRef.current.setVisible(activeBaseLayer === "DOF");
    }
  }, [mapObject, activeBaseLayer, selectedLayers, onFeatureClick]);

  // Update WMS layers when selectedLayers changes
  useEffect(() => {
    if (!mapObject) return;

    const geoserverUrl = process.env.REACT_APP_GEOSERVER_URL || "http://localhost:8080/geoserver";
    
    // Remove existing WMS layers (keep base layers)
    const layersToRemove = mapObject.getLayers().getArray().filter(
      (layer: BaseLayer) => {
        const title = layer.get("title");
        return title && title !== "OpenStreetMap" && title !== "Croatia DOF";
      }
    );
    layersToRemove.forEach((layer: BaseLayer) => mapObject.removeLayer(layer));

    // Add new WMS layers
    selectedLayers.forEach((layerName: string) => {
      const wmsLayer = new TileLayer({
        source: new TileWMS({
          url: `${geoserverUrl}/wms`,
          params: {
            LAYERS: `croatia:${layerName}`,
            FORMAT: "image/png",
            TRANSPARENT: true,
          },
          serverType: "geoserver",
          crossOrigin: "anonymous",
        }),
        visible: true,
      });
      wmsLayer.set("title", layerName);
      mapObject.addLayer(wmsLayer);
    });
  }, [mapObject, selectedLayers]);

  return <div ref={mapRef} className="w-full h-full" />;
};

export default MapCanvas;
