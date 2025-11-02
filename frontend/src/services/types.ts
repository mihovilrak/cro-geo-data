export interface LayerDescriptor {
  id: string;          // "cadastral_cadastralparcel"
  title: string;       // "Parcels"
  workspace?: string;  // "croatia" (optional)
  srid?: number;       // 3765 (optional)
}

export interface ParcelProperties {
  ogc_fid: number;
  parcel_id: string;
  cadastral_municipality: string;
  area_sqm: number;
  updated_at: string; // ISO Date
}

export interface BoundaryProperties {
  ogc_fid: number;
  name: string;
  admin_type: string;
  updated_at: string;
}

export interface DownloadMenuProps {
  activeLayer: string;  // e.g. "cadastral_cadastralparcel"
  bbox?: [number, number, number, number]; // [minX, minY, maxX, maxY] in EPSG:3857
}

export interface LayerSwitcherProps {
  availableLayers: { id: string; title: string }[];
  selectedLayers: string[];
  toggleLayer: (layerId: string) => void;
  toggleBase: (base: "OSM" | "DOF") => void;
  activeBase: "OSM" | "DOF";
}

export interface MapCanvasProps {
  selectedLayers: string[];       // e.g., ["cadastral_cadastralparcel", "cadastral_administrativeboundary"]
  onFeatureClick: (properties: any) => void;
  activeBaseLayer: "OSM" | "DOF";
}

export interface MetadataPopupProps {
  properties: Record<string, any> | null;
  onClose: () => void;
}