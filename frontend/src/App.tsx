import React, { useState, useEffect, useMemo } from "react";
import MapCanvas from "./components/MapCanvas";
import LayerSwitcher from "./components/LayerSwitcher";
import MetadataPopup from "./components/MetadataPopup";
import DownloadMenu from "./components/DownloadMenu";
import Navbar from "./components/Navbar";
import { fetchLayerCatalog, fetchLayerStats } from "./services/apiClient";
import { LayerDescriptor, LayerStats } from "./services/types";

const App: React.FC = () => {
  const [availableLayers, setAvailableLayers] = useState<LayerDescriptor[]>([]);
  const [selectedLayerIds, setSelectedLayerIds] = useState<string[]>([]);
  const [activeBase, setActiveBase] = useState<"OSM" | "DOF">("OSM");
  const [featureProps, setFeatureProps] = useState<any | null>(null);
  const [currentLayerId, setCurrentLayerId] = useState<string>("");
  const [layerError, setLayerError] = useState<string>();
  const [layerLoading, setLayerLoading] = useState<boolean>(false);
  const [layerStats, setLayerStats] = useState<Record<string, LayerStats>>({});
  const [featureInfoLoading, setFeatureInfoLoading] = useState<boolean>(false);
  const [featureInfoError, setFeatureInfoError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLayerLoading(true);

    Promise.all([fetchLayerCatalog(), fetchLayerStats()])
      .then(([layers, statsResponse]) => {
        if (!mounted) return;
        setAvailableLayers(layers);
        setLayerStats(statsResponse.layers);
        const defaults = layers.filter(
          (layer) => layer.default
        ).map((layer) => layer.id);
        setSelectedLayerIds(defaults);
        setCurrentLayerId(defaults[0] ?? "");
      })
      .catch((error) => {
        if (!mounted) return;
        console.error("Error loading layers:", error);
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
            layerStats={layerStats}
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
        <main className="flex-1 relative">
          {featureInfoLoading && (
            <div
              className="absolute top-4 left-1/2 transform -translate-x-1/2 z-50 bg-blue-500 text-white px-4 py-2 rounded shadow-lg flex items-center gap-2"
            >
              <svg
                className="animate-spin h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <span>Loading feature information...</span>
            </div>
          )}
          {featureInfoError && (
            <div
              className="absolute top-4 left-1/2 transform -translate-x-1/2 z-50 bg-red-500 text-white px-4 py-2 rounded shadow-lg flex items-center gap-2"
            >
              <span>⚠️</span>
              <span>{featureInfoError}</span>
              <button
                onClick={() => setFeatureInfoError(null)}
                className="ml-2 hover:bg-red-600 rounded px-2"
                aria-label="Dismiss"
              >
                ✕
              </button>
            </div>
          )}
          <MapCanvas
            selectedLayers={selectedLayerDescriptors}
            onFeatureClick={handleFeatureClick}
            activeBaseLayer={activeBase}
            onFeatureInfoLoading={setFeatureInfoLoading}
            onFeatureInfoError={setFeatureInfoError}
          />
        </main>
      </div>
    </div>
  );
};

export default App;
