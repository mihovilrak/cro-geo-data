import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const fetchParcels = async (
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
  const resp = await apiClient.get("/parcels/", { params });
  return resp.data;
}

export const fetchAdminBoundaries = async () => {
  const resp = await apiClient.get("/admin_boundaries/");
  return resp.data;
}

export default apiClient;
