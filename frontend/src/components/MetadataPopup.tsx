import React from "react";
import { MetadataPopupProps } from "../services/types";

const MetadataPopup: React.FC<MetadataPopupProps> = ({
  properties,
  onClose,
}) => {
  if (!properties) return null;
  
  return (
    <div className="fixed top-1/4 left-1/2 transform -translate-x-1/2 bg-white p-4 rounded shadow-lg z-50 w-80 max-h-96 overflow-hidden flex flex-col">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-lg">Feature Metadata</h3>
        <button 
          className="text-gray-600 hover:text-gray-800 text-xl font-bold" 
          onClick={onClose}
          aria-label="Close"
        >
          ✕
        </button>
      </div>
      <div className="text-sm overflow-y-auto flex-1">
        {Object.entries(properties).map(([key, value]) => (
          <div key={key} className="mb-2 flex flex-col border-b pb-2 last:border-0">
            <span className="font-medium text-gray-700">{key}:</span>
            <span className="ml-2 text-gray-900">{String(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetadataPopup;
