import { FormEvent, useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useToken } from "./hooks/useToken";

type HealthResponse = {
  service: string;
  status: string;
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

  const tokenQuery = useToken();

  const sessionsQuery = useQuery({
    queryKey: ["events", tokenQuery.data?.access_token],
    queryFn: () => fetchViewingSessions(tokenQuery.data!.access_token),
    enabled: Boolean(tokenQuery.data?.access_token)
  });

  const queryClient = useQueryClient();
  const [bookingForm, setBookingForm] = useState({
    eventId: "",
    seats: 1
  });

  const bookingMutation = useMutation({
    mutationFn: async () => {
      if (!tokenQuery.data) throw new Error("Missing token");
      const response = await fetch("/api/bookings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${tokenQuery.data.access_token}`
        },
        body: JSON.stringify({
          event_id: bookingForm.eventId,
          guest_id: "demo-user",
          seats: bookingForm.seats
        })
      });
      if (!response.ok) {
        throw new Error("Booking request failed");
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["events"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
    }
  });

  const analyticsQuery = useQuery({
    queryKey: ["stats"],
    queryFn: async () => {
      const response = await fetch("/analytics/stats");
      if (!response.ok) {
        throw new Error("Unable to load stats");
      }
      return response.json() as Promise<
        Array<{ event_id: string; total_seats: number; total_bookings: number }>
      >;
    }
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    bookingMutation.mutate();
  };

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
          <>
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
            <form onSubmit={handleSubmit} style={{ marginTop: "1rem" }}>
              <label>
                Session ID
                <select
                  value={bookingForm.eventId}
                  onChange={(e) =>
                    setBookingForm((prev) => ({ ...prev, eventId: e.target.value }))
                  }
                  required
                >
                  <option value="" disabled>
                    Choose session
                  </option>
                  {sessionsQuery.data.map((event) => (
                    <option key={event.id} value={event.id}>
                      {event.title} ({event.location})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Seats
                <input
                  type="number"
                  min={1}
                  value={bookingForm.seats}
                  onChange={(e) =>
                    setBookingForm((prev) => ({ ...prev, seats: Number(e.target.value) }))
                  }
                />
              </label>
              <button type="submit" disabled={bookingMutation.isLoading}>
                {bookingMutation.isLoading ? "Booking..." : "Book session"}
              </button>
              {bookingMutation.error instanceof Error && (
                <p style={{ color: "red" }}>{bookingMutation.error.message}</p>
              )}
              {bookingMutation.isSuccess && <p>Booking created!</p>}
            </form>
          </>
        )}
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2>Booking stats</h2>
        {analyticsQuery.isLoading && <p>Loading stats...</p>}
        {analyticsQuery.error instanceof Error && (
          <p style={{ color: "red" }}>{analyticsQuery.error.message}</p>
        )}
        {analyticsQuery.data && (
          <ul>
            {analyticsQuery.data.map((stat) => (
              <li key={stat.event_id}>
                {stat.event_id}: {stat.total_bookings} bookings / {stat.total_seats} seats
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
