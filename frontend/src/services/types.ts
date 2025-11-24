export interface LayerDescriptor {
  id: string;
  title: string;
  wms_name: string;
  api_path?: string;
  workspace?: string;
  native_table?: string;
  default?: boolean;
}

export interface ParcelProperties {
  ogc_fid: number;
  parcel_id: string;
  cadastral_municipality: string;
  area_sqm: number;
  updated_at: string;
}

export interface BoundaryProperties {
  ogc_fid: number;
  name: string;
  admin_type: string;
  updated_at: string;
}

export interface DownloadMenuProps {
  activeLayer: LayerDescriptor;
  bbox?: [number, number, number, number];
}

export interface LayerSwitcherProps {
  availableLayers: LayerDescriptor[];
  selectedLayers: string[];
  toggleBase: (base: "OSM" | "DOF") => void;
  activeBase: "OSM" | "DOF";
  toggleLayer: (layerId: string) => void;
  isLoading: boolean;
  error?: string;
}

export interface MapCanvasProps {
  selectedLayers: LayerDescriptor[];
  onFeatureClick: (properties: any) => void;
  activeBaseLayer: "OSM" | "DOF";
}

export interface MetadataPopupProps {
  properties: Record<string, any> | null;
  onClose: () => void;
}