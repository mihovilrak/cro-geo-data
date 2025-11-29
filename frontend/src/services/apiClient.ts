import axios from "axios";
import { LayerDescriptor } from "./types";

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const fetchCadastralParcels = async (
  bbox?: [number, number, number, number],
  filters?: Record<string, string>
) => {
  const params: any = {};
  if (bbox) {
    params.bbox = bbox.join(",");
  }
  if (filters) {
    Object.assign(params, filters);
  }
  const resp = await apiClient.get("/cadastral_parcels/", { params });
  return resp.data;
}

export const fetchCounties = async (
  bbox?: [number, number, number, number],
  filters?: Record<string, string>
) => {
  const params: any = {};
  if (bbox) {
    params.bbox = bbox.join(",");
  }
  if (filters) {
    Object.assign(params, filters);
  }
  const resp = await apiClient.get("/counties/", { params });
  return resp.data;
}

export const fetchMunicipalities = async (
  bbox?: [number, number, number, number],
  filters?: Record<string, string>
) => {
  const params: any = {};
  if (bbox) {
    params.bbox = bbox.join(",");
  }
  if (filters) {
    Object.assign(params, filters);
  }
  const resp = await apiClient.get("/municipalities/", { params });
  return resp.data;
}

export const fetchSettlements = async (
  bbox?: [number, number, number, number],
  filters?: Record<string, string>
) => {
  const params: any = {};
  if (bbox) {
    params.bbox = bbox.join(",");
  }
  if (filters) {
    Object.assign(params, filters);
  }
  const resp = await apiClient.get("/settlements/", { params });
  return resp.data;
}

export const fetchStreets = async (
  bbox?: [number, number, number, number],
  filters?: Record<string, string>
) => {
  const params: any = {};
  if (bbox) {
    params.bbox = bbox.join(",");
  }
  if (filters) {
    Object.assign(params, filters);
  }
  const resp = await apiClient.get("/streets/", { params });
  return resp.data;
}

export const fetchAddresses = async (
  bbox?: [number, number, number, number],
  filters?: Record<string, string>
) => {
  const params: any = {};
  if (bbox) {
    params.bbox = bbox.join(",");
  }
  if (filters) {
    Object.assign(params, filters);
  }
  const resp = await apiClient.get("/addresses/", { params });
  return resp.data;
}

export const fetchLayerCatalog = async (): Promise<LayerDescriptor[]> => {
  const resp = await apiClient.get("/layers/");
  return resp.data;
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

export const fetchLayerStats = async (): Promise<LayerStatsResponse> => {
  const resp = await apiClient.get("/layers/stats/");
  return resp.data;
};

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

export const getFeatureInfo = async (
  params: GetFeatureInfoParams
): Promise<GetFeatureInfoResponse> => {
  const queryParams: Record<string, string> = {
    lat: params.lat.toString(),
    lon: params.lon.toString(),
  };

  if (params.layer) {
    queryParams.layer = params.layer;
  }

  if (params.tolerance !== undefined) {
    queryParams.tolerance = params.tolerance.toString();
  }

  if (params.srid !== undefined) {
    queryParams.srid = params.srid.toString();
  }

  const resp = await apiClient.get("/features/info/", { params: queryParams });
  return resp.data;
}

export default apiClient;
