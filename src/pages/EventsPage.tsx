import { useState, useEffect } from "react";
import { getEvents } from "../api";

interface SecurityEvent {
  id: string;
  timestamp: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  title: string;
  description: string;
  assetHostname: string;
  assetIp: string;
  sourceIp: string;
  tags: string[];
  userId?: string;
}

export default function EventsPage() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getEvents();
      if (data.error) {
        setError(data.error);
      } else {
        setEvents(data || []);
      }
    } catch (err) {
      setError("Failed to load events");
    } finally {
      setLoading(false);
    }
  };

  const filtered = events.filter((e) => {
    const matchesSearch =
      e.title.toLowerCase().includes(search.toLowerCase()) ||
      e.description.toLowerCase().includes(search.toLowerCase()) ||
      e.assetHostname.toLowerCase().includes(search.toLowerCase());
    const matchesSeverity = severityFilter === "ALL" || e.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  const severityColor = (s: string) => {
    if (s === "CRITICAL") return "#cc0000";
    if (s === "HIGH") return "red";
    if (s === "MEDIUM") return "orange";
    return "green";
  };

  return (
    <div className="page-container">
      <h1>Security Events</h1>

      {error && <p style={{ color: "red", marginBottom: 12 }}>{error}</p>}

      <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "center" }}>
        <input
          type="text"
          placeholder="Search events..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: "100%", maxWidth: 400 }}
          disabled={loading}
        />
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          style={{ width: 140 }}
          disabled={loading}
        >
          <option value="ALL">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {search && (
        <p>
          Showing results for: <strong>{search}</strong> ({filtered.length} events)
        </p>
      )}

      {loading ? (
        <p style={{ color: "#999" }}>Loading events...</p>
      ) : (
        <>
          <table>
            <thead>
              <tr>
                <th>Severity</th>
                <th>Title</th>
                <th>Asset</th>
                <th>Source IP</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((event) => (
                <tr
                  key={event.id}
                  onClick={() => setSelectedEvent(event)}
                  style={{ cursor: "pointer" }}
                >
                  <td style={{ color: severityColor(event.severity), fontWeight: 600 }}>
                    {event.severity}
                  </td>
                  <td>{event.title}</td>
                  <td style={{ fontFamily: "monospace", fontSize: 13 }}>
                    {event.assetHostname}
                  </td>
                  <td style={{ fontFamily: "monospace", fontSize: 13 }}>
                    {event.sourceIp || "(none)"}
                  </td>
                  <td style={{ fontSize: 13 }}>
                    {new Date(event.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filtered.length === 0 && <p style={{ color: "#999" }}>No events found.</p>}

          <div style={{ marginTop: 12 }}>
            <button
              onClick={() => {
                const blob = new Blob([JSON.stringify(filtered, null, 2)], {
                  type: "application/json",
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "penguwave_events_export.json";
                a.click();
                URL.revokeObjectURL(url);
              }}
              style={{ fontSize: 13 }}
            >
              Export Events (JSON)
            </button>
          </div>
        </>
      )}

      {/* Inline event detail */}
      {selectedEvent && (
        <div className="event-detail">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2>{selectedEvent.title}</h2>
            <button onClick={() => setSelectedEvent(null)} style={{ cursor: "pointer" }}>
              Close
            </button>
          </div>
          <p>
            <strong>Severity:</strong>{" "}
            <span style={{ color: severityColor(selectedEvent.severity) }}>
              {selectedEvent.severity}
            </span>
          </p>
          <p>
            <strong>Description:</strong>
          </p>
          <p>{selectedEvent.description}</p>
          <p>
            <strong>Asset:</strong> {selectedEvent.assetHostname} ({selectedEvent.assetIp})
          </p>
          <p>
            <strong>Source IP:</strong> {selectedEvent.sourceIp || "(none)"}
          </p>
          <p>
            <strong>Tags:</strong> {selectedEvent.tags.join(", ")}
          </p>
          <p>
            <strong>Timestamp:</strong> {new Date(selectedEvent.timestamp).toLocaleString()}
          </p>
          <h3>Raw Event Data</h3>
          <pre>{JSON.stringify(selectedEvent, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
