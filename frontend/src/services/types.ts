export interface LayerDescriptor {
  id: string;
  title: string;
  wms_name: string;
  api_path?: string;
  workspace?: string;
  native_table?: string;
  default?: boolean;
}

export interface LayerStats {
  count: number | null;
  last_updated: string | null;
  freshness_days: number | null;
  error?: string;
}

export interface LayerStatsResponse {
  layers: Record<string, LayerStats>;
}

export interface GetFeatureInfoParams {
  lat: number;
  lon: number;
  layer?: string;
  tolerance?: number;
  srid?: number;
}

export interface GetFeatureInfoResponse {
  type: "FeatureCollection";
  features: any[];
  query: {
    lat: number;
    lon: number;
    layer?: string;
    tolerance?: string;
  };
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
  layerStats?: Record<string, LayerStats>;
}

export interface MapCanvasProps {
  selectedLayers: LayerDescriptor[];
  onFeatureClick: (properties: any) => void;
  activeBaseLayer: "OSM" | "DOF";
  onFeatureInfoLoading?: (loading: boolean) => void;
  onFeatureInfoError?: (error: string | null) => void;
}

export interface MetadataPopupProps {
  properties: Record<string, any> | null;
  onClose: () => void;
}