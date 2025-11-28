import { test, expect } from "@playwright/test";

const API_BASE = process.env.COUCHANNEL_BASE_URL ?? "http://localhost:8000";

const getToken = async () => {
  const response = await fetch(`${API_BASE}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: "e2e-user" })
  });
  if (!response.ok) {
    throw new Error("Unable to fetch token");
  }
  return response.json();
};

test("health + aggregated events", async ({ request }) => {
  const health = await request.get(`${API_BASE}/healthz`);
  expect(health.ok()).toBeTruthy();
  const healthPayload = await health.json();
  expect(healthPayload.service).toBe("api");

  const token = await getToken();
  const events = await request.get(`${API_BASE}/events/aggregated`, {
    headers: { Authorization: `Bearer ${token.access_token}` }
  });
  expect(events.ok()).toBeTruthy();
});
