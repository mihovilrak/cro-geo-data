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

export default apiClient;
