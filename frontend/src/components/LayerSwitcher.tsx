// src/components/LayerSwitcher.tsx
import React from "react";
import { LayerSwitcherProps } from "../services/types";

const LayerSwitcher: React.FC<LayerSwitcherProps> = ({
  availableLayers,
  selectedLayers,
  toggleLayer,
  toggleBase,
  activeBase,
  isLoading,
  error,
}) => {
  return (
    <div className="bg-white p-4 rounded shadow mb-2">
      <h3 className="font-semibold mb-2 text-lg">Background Layer</h3>
      <div className="flex items-center mb-4">
        <label className="mr-4 flex items-center cursor-pointer">
          <input
            type="radio"
            name="baseLayer"
            checked={activeBase === "OSM"}
            onChange={() => toggleBase("OSM")}
            className="mr-2"
          />
          <span>OpenStreetMap</span>
        </label>
        <label className="flex items-center cursor-pointer">
          <input
            type="radio"
            name="baseLayer"
            checked={activeBase === "DOF"}
            onChange={() => toggleBase("DOF")}
            className="mr-2"
          />
          <span>DOF</span>
        </label>
      </div>
      <h3 className="font-semibold mb-2 text-lg">Data Layers</h3>
      <div className="space-y-2">
        {isLoading && (
          <p className="text-gray-500 text-sm">Loading layers…</p>
        )}
        {!isLoading && error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}
        {!isLoading && !error && availableLayers.length === 0 && (
          <p className="text-gray-500 text-sm">No layers available</p>
        )}
        {!isLoading && !error && availableLayers.length > 0 && (
          availableLayers.map((layer) => (
            <label key={layer.id} className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={selectedLayers.includes(layer.id)}
                onChange={() => toggleLayer(layer.id)}
                className="mr-2"
              />
              <span>{layer.title}</span>
            </label>
          ))
        )
        }
      </div>
    </div>
  );
};

export default LayerSwitcher;
