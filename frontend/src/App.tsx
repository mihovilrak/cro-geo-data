// src/App.tsx
import React, { useState, useEffect, useMemo } from "react";
import MapCanvas from "./components/MapCanvas";
import LayerSwitcher from "./components/LayerSwitcher";
import MetadataPopup from "./components/MetadataPopup";
import DownloadMenu from "./components/DownloadMenu";
import Navbar from "./components/Navbar";
import { fetchLayerCatalog } from "./services/apiClient";
import { LayerDescriptor } from "./services/types";

const App: React.FC = () => {
  const [availableLayers, setAvailableLayers] = useState<LayerDescriptor[]>([]);
  const [selectedLayerIds, setSelectedLayerIds] = useState<string[]>([]);
  const [activeBase, setActiveBase] = useState<"OSM" | "DOF">("OSM");
  const [featureProps, setFeatureProps] = useState<any | null>(null);
  const [currentLayerId, setCurrentLayerId] = useState<string>("");
  const [layerError, setLayerError] = useState<string>();
  const [layerLoading, setLayerLoading] = useState<boolean>(false);

  useEffect(() => {
    let mounted = true;
    setLayerLoading(true);
    fetchLayerCatalog()
      .then((layers) => {
        if (!mounted) return;
        setAvailableLayers(layers);
        const defaults = layers.filter((layer) => layer.default).map((layer) => layer.id);
        setSelectedLayerIds(defaults);
        setCurrentLayerId(defaults[0] ?? "");
      })
      .catch(() => {
        if (!mounted) return;
        setLayerError("Unable to load layer catalog");
      })
      .finally(() => mounted && setLayerLoading(false));
    return () => {
      mounted = false;
    };
  }, []);

  const selectedLayerDescriptors = useMemo(
    () => availableLayers.filter((layer) => selectedLayerIds.includes(layer.id)),
    [availableLayers, selectedLayerIds]
  );

  const currentLayerDescriptor = useMemo(
    () => selectedLayerDescriptors.find((layer) => layer.id === currentLayerId),
    [selectedLayerDescriptors, currentLayerId]
  );

  const toggleLayer = (layerId: string) => {
    setFeatureProps(null);
    if (selectedLayerIds.includes(layerId)) {
      const updated = selectedLayerIds.filter((l) => l !== layerId);
      setSelectedLayerIds(updated);
      if (currentLayerId === layerId) {
        setCurrentLayerId(updated[0] ?? "");
      }
    } else {
      const updated = [...selectedLayerIds, layerId];
      setSelectedLayerIds(updated);
      setCurrentLayerId(layerId);
    }
  };

  const toggleBase = (base: "OSM" | "DOF") => {
    setActiveBase(base);
  };

  const handleFeatureClick = (props: any) => {
    setFeatureProps(props);
  };

  const [bbox] = useState<[number, number, number, number]>();

  return (
    <div className="h-screen flex flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <aside className="w-64 border-r p-4 overflow-y-auto bg-gray-50">
          <LayerSwitcher
            availableLayers={availableLayers}
            selectedLayers={selectedLayerIds}
            toggleLayer={toggleLayer}
            toggleBase={toggleBase}
            activeBase={activeBase}
            isLoading={layerLoading}
            error={layerError}
          />
          {featureProps && (
            <MetadataPopup
              properties={featureProps}
              onClose={() => setFeatureProps(null)}
            />
          )}
          {currentLayerDescriptor && (
            <DownloadMenu activeLayer={currentLayerDescriptor} bbox={bbox} />
          )}
        </aside>
        <main className="flex-1">
          <MapCanvas
            selectedLayers={selectedLayerDescriptors}
            onFeatureClick={handleFeatureClick}
            activeBaseLayer={activeBase}
          />
        </main>
      </div>
    </div>
  );
};

export default App;
