import React, { useMemo } from "react";
import { MetadataPopupProps } from "../services/types";
import { formatDate, formatNumber } from "../utils/format";

const HIDDEN_FIELDS = ["_layer", "geom", "geometry"];
const DATE_FIELDS = ["updated_at", "last_updated", "created_at"];
const NUMBER_FIELDS = [
  "area_sqm",
  "graphical_area",
  "id",
  "ogc_fid",
  "national_code",
  "county_code",
  "municipality_code",
  "settlement_code",
];

const FIELD_DISPLAY_NAMES: Record<string, string> = {
  _layer_title: "Layer",
  parcel_code: "Parcel Code",
  cadastral_municipality: "Cadastral Municipality",
  cadastral_municipality_name: "Cadastral Municipality",
  county_name: "County",
  municipality_name: "Municipality",
  settlement_name: "Settlement",
  name: "Name",
  updated_at: "Last Updated",
  area_sqm: "Area (m²)",
  graphical_area: "Area (m²)",
};

const MetadataPopup: React.FC<MetadataPopupProps> = ({
  properties,
  onClose,
}) => {
  const { title, groupedProperties, otherProperties } = useMemo(() => {
    if (!properties) {
      return { title: "Feature Metadata", groupedProperties: [], otherProperties: [] };
    }

    const layerTitle = properties._layer_title || properties._layer || null;
    const title = layerTitle ? `${layerTitle} Details` : "Feature Metadata";

    const adminFields = ["county_name", "municipality_name", "settlement_name"];
    const grouped: Array<{ label: string; value: any }> = [];
    const others: Array<{ key: string; label: string; value: any }> = [];

    Object.entries(properties).forEach(([key, value]) => {
      if (HIDDEN_FIELDS.includes(key)) {
        return;
      }

      const displayName = FIELD_DISPLAY_NAMES[key]
        || key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
      
      let formattedValue = value;
      if (value === null || value === undefined) {
        formattedValue = "N/A";
      } else if (DATE_FIELDS.includes(key) && typeof value === "string") {
        formattedValue = formatDate(value);
      } else if (NUMBER_FIELDS.includes(key) && typeof value === "number") {
        formattedValue = formatNumber(value);
      } else {
        formattedValue = String(value);
      }

      if (adminFields.includes(key)) {
        grouped.push({ label: displayName, value: formattedValue });
      } else {
        others.push({ key, label: displayName, value: formattedValue });
      }
    });

    return { title, groupedProperties: grouped, otherProperties: others };
  }, [properties]);

  if (!properties) return null;

  return (
    <div
      className="fixed top-1/4 left-1/2 transform -translate-x-1/2 bg-white p-4 rounded shadow-lg z-50 w-96 max-h-[80vh] overflow-hidden flex flex-col border border-gray-200"
    >
      <div className="flex justify-between items-center mb-3 pb-2 border-b">
        <h3 className="font-semibold text-lg">{title}</h3>
        <button
          className="text-gray-600 hover:text-gray-800 text-xl font-bold w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100"
          onClick={onClose}
          aria-label="Close"
        >
          ✕
        </button>
      </div>
      <div className="text-sm overflow-y-auto flex-1">
        {groupedProperties.length > 0 && (
          <div className="mb-4 pb-3 border-b">
            <h4
              className="font-semibold text-gray-700 mb-2 text-xs uppercase tracking-wide"
            >Administrative Hierarchy</h4>
            <div className="space-y-1">
              {groupedProperties.map((item, idx) => (
                <div key={idx} className="flex justify-between">
                  <span className="text-gray-600">{item.label}:</span>
                  <span className="font-medium text-gray-900">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="space-y-2">
          {otherProperties.map((item) => (
            <div key={item.key} className="flex flex-col border-b pb-2 last:border-0">
              <span
                className="font-medium text-gray-700 text-xs uppercase tracking-wide mb-1"
              >{item.label}</span>
              <span className="text-gray-900 break-words">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MetadataPopup;
