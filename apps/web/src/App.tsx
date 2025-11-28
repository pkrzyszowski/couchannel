import { useQuery } from "@tanstack/react-query";

type HealthResponse = {
  service: string;
  status: string;
};

type TokenResponse = {
  access_token: string;
  token_type: string;
};

type ViewingSessionDTO = {
  id: string;
  title: string;
  starts_at: string;
  location: string;
  price_pln: number;
  host: {
    display_name: string;
    reputation: number;
  };
};

const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await fetch("/api/healthz");
  if (!response.ok) {
    throw new Error("Unable to reach API");
  }
  return response.json();
};

const fetchToken = async (): Promise<TokenResponse> => {
  const response = await fetch("/api/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: "demo-user" })
  });
  if (!response.ok) {
    throw new Error("Unable to obtain token");
  }
  return response.json();
};

const fetchViewingSessions = async (token: string): Promise<ViewingSessionDTO[]> => {
  const response = await fetch("/api/events/aggregated", {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!response.ok) {
    throw new Error("Unable to load events");
  }
  return response.json();
};

export default function App() {
  const { data: health, isLoading, error } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth
  });

  const tokenQuery = useQuery({
    queryKey: ["token"],
    queryFn: fetchToken
  });

  const sessionsQuery = useQuery({
    queryKey: ["events", tokenQuery.data?.access_token],
    queryFn: () => fetchViewingSessions(tokenQuery.data!.access_token),
    enabled: Boolean(tokenQuery.data?.access_token)
  });

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <h1>couchannel</h1>
      <p>Hosts share premium streams & seats just like BlaBlaCar shares rides.</p>
      {isLoading && <p>Connecting to API...</p>}
      {error instanceof Error && <p style={{ color: "red" }}>{error.message}</p>}
      {health && (
        <p>
          Backend `{health.service}` status <strong>{health.status}</strong>.
        </p>
      )}

      <section style={{ marginTop: "2rem" }}>
        <h2>Upcoming shared sessions</h2>
        {tokenQuery.isLoading && <p>Requesting demo token...</p>}
        {tokenQuery.error instanceof Error && (
          <p style={{ color: "red" }}>{tokenQuery.error.message}</p>
        )}
        {sessionsQuery.isLoading && tokenQuery.data && <p>Loading sessions...</p>}
        {sessionsQuery.error instanceof Error && (
          <p style={{ color: "red" }}>{sessionsQuery.error.message}</p>
        )}
        {sessionsQuery.data && (
          <ul>
            {sessionsQuery.data.map((event) => (
              <li key={event.id} style={{ marginBottom: "1rem" }}>
                <strong>{event.title}</strong> — {event.location} — {" "}
                <em>{new Date(event.starts_at).toLocaleString()}</em>
                <br />
                Host {event.host.display_name} (rep. {event.host.reputation}) · {" "}
                {event.price_pln} PLN / seat
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
