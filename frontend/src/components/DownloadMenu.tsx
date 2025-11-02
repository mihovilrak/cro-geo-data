// src/components/DownloadMenu.tsx
import React, { useState } from "react";
import { DownloadMenuProps } from "../services/types";

const DownloadMenu: React.FC<DownloadMenuProps> = ({ activeLayer, bbox }) => {
  const [format, setFormat] = useState<string>("application/json");

  // Map user-friendly labels to GeoServer WFS outputFormat params
  const formatOptions = [
    { label: "GeoJSON", value: "application/json" },
    { label: "Shapefile (zip)", value: "shape-zip" },
    { label: "KML", value: "KML" },
    { label: "DXF", value: "application/dxf" },
    { label: "GPKG", value: "application/geopackage+sqlite3" },
    { label: "CSV", value: "text/csv" },
  ];

  const buildWfsUrl = () => {
    const base = `${process.env.REACT_APP_GEOSERVER_URL || "http://localhost:8080/geoserver"}/wfs`;
    const params = new URLSearchParams({
      service: "WFS",
      version: "1.1.0",
      request: "GetFeature",
      typeName: `croatia:${activeLayer}`,
      outputFormat: format,
    });
    if (bbox) {
      params.append("bbox", bbox.join(",") + ",EPSG:3857");
    }
    return `${base}?${params.toString()}`;
  };

  return (
    <div className="bg-white p-4 rounded shadow mt-2">
      <h4 className="font-semibold mb-2 text-lg">Download "{activeLayer}"</h4>
      <div className="flex flex-col space-y-2">
        <select
          className="border p-2 rounded"
          value={format}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFormat(e.target.value)}
        >
          {formatOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <a
          href={buildWfsUrl()}
          target="_blank"
          rel="noreferrer"
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded text-center transition"
        >
          Download
        </a>
      </div>
    </div>
  );
};

export default DownloadMenu;
