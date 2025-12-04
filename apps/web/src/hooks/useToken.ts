import { useQuery } from "@tanstack/react-query";

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export const useToken = () =>
  useQuery({
    queryKey: ["token"],
    queryFn: async (): Promise<TokenResponse> => {
      const response = await fetch("/api/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "demo-user" })
      });
      if (!response.ok) {
        throw new Error("Unable to obtain token");
      }
      return response.json();
    }
  });
