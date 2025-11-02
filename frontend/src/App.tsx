// src/App.tsx
import React, { useState, useEffect } from "react";
import MapCanvas from "./components/MapCanvas";
import LayerSwitcher from "./components/LayerSwitcher";
import MetadataPopup from "./components/MetadataPopup";
import DownloadMenu from "./components/DownloadMenu";
import Navbar from "./components/Navbar";

const App: React.FC = () => {
  const [availableLayers, setAvailableLayers] = useState<
    { id: string; title: string }[]
  >([]);
  const [selectedLayers, setSelectedLayers] = useState<string[]>([]);
  const [activeBase, setActiveBase] = useState<"OSM" | "DOF">("OSM");
  const [featureProps, setFeatureProps] = useState<any | null>(null);
  const [currentLayer, setCurrentLayer] = useState<string>("");

  useEffect(() => {
    // Fetch list of layers from GeoServer REST API or hardcode for now
    // TODO: Replace with actual API call when backend is ready
    setAvailableLayers([
      { id: "cadastral_cadastralparcel", title: "Cadastral Parcels" },
      { id: "cadastral_administrativeboundary", title: "Administrative Boundaries" },
    ]);
  }, []);

  const toggleLayer = (layerId: string) => {
    setFeatureProps(null);
    if (selectedLayers.includes(layerId)) {
      setSelectedLayers(selectedLayers.filter((l) => l !== layerId));
      if (currentLayer === layerId) setCurrentLayer("");
    } else {
      setSelectedLayers([...selectedLayers, layerId]);
      setCurrentLayer(layerId);
    }
  };

  const toggleBase = (base: "OSM" | "DOF") => {
    setActiveBase(base);
  };

  const handleFeatureClick = (props: any) => {
    setFeatureProps(props);
  };

  // Optional: compute current map extent → pass as bbox to DownloadMenu
  const [bbox] = useState<[number, number, number, number]>();

  return (
    <div className="h-screen flex flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <aside className="w-64 border-r p-4 overflow-y-auto bg-gray-50">
          <LayerSwitcher
            availableLayers={availableLayers}
            selectedLayers={selectedLayers}
            toggleLayer={toggleLayer}
            toggleBase={toggleBase}
            activeBase={activeBase}
          />
          {featureProps && (
            <MetadataPopup
              properties={featureProps}
              onClose={() => setFeatureProps(null)}
            />
          )}
          {currentLayer && (
            <DownloadMenu activeLayer={currentLayer} bbox={bbox} />
          )}
        </aside>
        <main className="flex-1">
          <MapCanvas
            selectedLayers={selectedLayers}
            onFeatureClick={handleFeatureClick}
            activeBaseLayer={activeBase}
          />
        </main>
      </div>
    </div>
  );
};

export default App;
