import React from "react";
import { LayerSwitcherProps } from "../services/types";
import {
  formatNumber,
  getFreshnessColor,
  getFreshnessText,
} from "../utils/format";

const LayerSwitcher: React.FC<LayerSwitcherProps> = ({
  availableLayers,
  selectedLayers,
  toggleLayer,
  toggleBase,
  activeBase,
  isLoading,
  error,
  layerStats,
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
          availableLayers.map((layer) => {
            const stats = layerStats?.[layer.id];
            return (
              <div key={layer.id} className="mb-3 pb-2 border-b last:border-0">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedLayers.includes(layer.id)}
                    onChange={() => toggleLayer(layer.id)}
                    className="mr-2"
                  />
                  <span className="font-medium">{layer.title}</span>
                </label>
                {stats && (
                  <div className="ml-6 mt-1 text-xs text-gray-600 space-y-1">
                    {stats.count !== null && (
                      <div>
                        <span className="font-medium">Count:</span>{" "}
                        {formatNumber(stats.count)}
                      </div>
                    )}
                    {stats.freshness_days !== null && (
                      <div>
                        <span className="font-medium">Updated:</span>{" "}
                        <span className={getFreshnessColor(stats.freshness_days)}>
                          {getFreshnessText(stats.freshness_days)}
                        </span>
                      </div>
                    )}
                    {stats.error && (
                      <div className="text-red-600">
                        <span className="font-medium">Error:</span> {stats.error}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default LayerSwitcher;
