import type { AuthBindings } from "@refinedev/core";
import { apiClient } from "./apiClient";

const TOKEN_KEY = "cctv_token";
const ROLE_KEY = "cctv_role";
const USERNAME_KEY = "cctv_username";

type LoginParams = { username: string; password: string };

export const authProvider = (): AuthBindings => ({
  login: async ({ username, password }: LoginParams) => {
    const response = await apiClient.post("/auth/login", { username, password });
    const { token, role } = response.data;
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(ROLE_KEY, role);
    localStorage.setItem(USERNAME_KEY, username);
    return {
      success: true,
      redirectTo: "/",
    };
  },
  logout: async () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
    localStorage.removeItem(USERNAME_KEY);
    return {
      success: true,
      redirectTo: "/login",
    };
  },
  check: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      return {
        authenticated: true,
      };
    }
    return {
      authenticated: false,
      redirectTo: "/login",
      logout: true,
    };
  },
  getPermissions: async () => {
    return localStorage.getItem(ROLE_KEY) ?? "normal";
  },
  getIdentity: async () => {
    const username = localStorage.getItem(USERNAME_KEY);
    if (!username) return null;
    return {
      name: username,
      avatar: undefined,
    };
  },
});
