import type {
  CreateParams,
  DataProvider,
  DeleteOneParams,
  GetListParams,
  GetOneParams,
  CustomParams,
  UpdateParams,
} from "@refinedev/core";
import { apiClient, API_URL } from "./apiClient";

const resourceMap: Record<string, string> = {
  alerts: "/alerts/recent",
  "verified-alerts": "/alerts/verified",
};

export const dataProvider = (apiUrl: string = API_URL): DataProvider => ({
  getList: async ({ resource }: GetListParams) => {
    const endpoint = resourceMap[resource] ?? `/${resource}`;
    const response = await apiClient.get(`${endpoint}`);
    const data = response.data?.alerts ?? [];
    return {
      data,
      total: data.length,
    };
  },

  getOne: async ({ resource, id }: GetOneParams) => {
    const response = await apiClient.get(`/${resource}/${id}`);
    return { data: response.data };
  },

  update: async ({ resource, id, variables }: UpdateParams) => {
    const endpoint = resource === "alerts" ? `/alerts/${id}/verify` : `/${resource}/${id}`;
    const response = await apiClient.post(endpoint, variables);
    return { data: response.data };
  },

  create: async ({ resource, variables }: CreateParams) => {
    const response = await apiClient.post(`/${resource}`, variables);
    return { data: response.data };
  },

  deleteOne: async ({ resource, id }: DeleteOneParams) => {
    const response = await apiClient.delete(`/${resource}/${id}`);
    return { data: response.data };
  },

  getApiUrl: () => apiUrl,

  custom: async ({ url, method, payload, headers, meta }: CustomParams) => {
    const response = await apiClient.request({
      url,
      method: method?.toLowerCase(),
      data: payload || meta?.body,
      headers,
      params: meta?.query,
    });
    return { data: response.data };
  },
});
