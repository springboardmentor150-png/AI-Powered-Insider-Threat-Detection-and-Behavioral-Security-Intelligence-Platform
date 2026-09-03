import api from "@/lib/api";

export type AuthUser = {
  user_id: string | number;
  role: string;
};

export async function verifyAuthentication(): Promise<AuthUser> {
  const token = localStorage.getItem("itbis-token");

  if (!token) {
    throw new Error("No authentication token found");
  }

  const response = await api.get("/auth/me");

  return response.data;
}

export function clearAuthentication() {
  localStorage.removeItem("itbis-token");
  localStorage.removeItem("itbis-user");
}