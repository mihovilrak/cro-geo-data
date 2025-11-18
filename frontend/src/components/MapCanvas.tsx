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
import { LayerDescriptor, MapCanvasProps } from "../services/types";

const MapCanvas: React.FC<MapCanvasProps> = ({
  selectedLayers,
  onFeatureClick,
  activeBaseLayer,
}) => {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const [mapObject, setMapObject] = useState<Map | null>(null);
  const osmLayerRef = useRef<TileLayer<OSM> | null>(null);
  const dofLayerRef = useRef<TileLayer<TileWMS> | null>(null);
  const workspace =
    process.env.REACT_APP_GEOSERVER_WORKSPACE || "cro-geo-data";

  useEffect(() => {
    if (!mapObject && mapRef.current) {
      const osmLayer = new TileLayer({
        source: new OSM(),
        visible: activeBaseLayer === "OSM",
      });
      osmLayer.set("title", "OpenStreetMap");
      osmLayerRef.current = osmLayer;

      const geoserverUrl =
        process.env.REACT_APP_GEOSERVER_URL || "http://localhost:8080/geoserver";

      const dofLayer = new TileLayer({
        source: new TileWMS({
          url: `${geoserverUrl}/wms`,
          params: {
            LAYERS: `${workspace}:dof_ortho`,
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

      initialMap.on("singleclick", async (evt) => {
        const viewResolution = initialMap.getView().getResolution();
        const coordinate = evt.coordinate;
        
        if (selectedLayers.length > 0 && viewResolution) {
          const descriptor = selectedLayers[0];
          const wmsLayers = initialMap
            .getLayers()
            .getArray()
            .filter(
              (candidate: BaseLayer) => candidate.get("title") === descriptor.id
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
                  QUERY_LAYERS: `${descriptor.workspace || workspace}:${descriptor.wms_name}` 
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
 
    if (mapObject && osmLayerRef.current && dofLayerRef.current) {
      osmLayerRef.current.setVisible(activeBaseLayer === "OSM");
      dofLayerRef.current.setVisible(activeBaseLayer === "DOF");
    }
  }, [mapObject, activeBaseLayer, selectedLayers, onFeatureClick]);

  useEffect(() => {
    if (!mapObject) return;

    const geoserverUrl = process.env.REACT_APP_GEOSERVER_URL || "http://localhost:8080/geoserver";

    const layersToRemove = mapObject.getLayers().getArray().filter(
      (layer: BaseLayer) => {
        const title = layer.get("title");
        return title && title !== "OpenStreetMap" && title !== "Croatia DOF";
      }
    );
    layersToRemove.forEach((layer: BaseLayer) => mapObject.removeLayer(layer));

    selectedLayers.forEach((layer: LayerDescriptor) => {
      const layerWorkspace = layer.workspace || workspace;
      const wmsLayer = new TileLayer({
        source: new TileWMS({
          url: `${geoserverUrl}/wms`,
          params: {
            LAYERS: `${layerWorkspace}:${layer.wms_name}`,
            FORMAT: "image/png",
            TRANSPARENT: true,
          },
          serverType: "geoserver",
          crossOrigin: "anonymous",
        }),
        visible: true,
      });
      wmsLayer.set("title", layer.id);
      mapObject.addLayer(wmsLayer);
    });
  }, [mapObject, selectedLayers, workspace]);

  return <div ref={mapRef} className="w-full h-full" />;
};

export default MapCanvas;
