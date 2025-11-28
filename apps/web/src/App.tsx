import { useQuery } from "@tanstack/react-query";

type HealthResponse = {
  service: string;
  status: string;
};

const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await fetch("/api/healthz");
  if (!response.ok) {
    throw new Error("Unable to reach API");
  }
  return response.json();
};

export default function App() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth
  });

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <h1>couchannel</h1>
      <p>Połącz gospodarzy i gości, aby wspólnie oglądać topowe rozgrywki.</p>
      {isLoading && <p>Łączenie z API...</p>}
      {error instanceof Error && <p style={{ color: "red" }}>{error.message}</p>}
      {data && (
        <p>
          Backend `{data.service}` zgłasza status <strong>{data.status}</strong>.
        </p>
      )}
    </main>
  );
}
