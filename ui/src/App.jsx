import React, { useState, useEffect } from "react";
import axios from "axios";
import { Pie, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from "chart.js";
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
);

const API_URL = "http://localhost:8003";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [packets, setPackets] = useState([]);
  const [timeline, setTimeline] = useState({ times: [], counts: [] });
  const [protocolChart, setProtocolChart] = useState({ labels: [], counts: [] });

  const fetchAll = async () => {
    try {
      const [p1, p2, p3] = await Promise.all([
        axios.get(`${API_URL}/packets`),
        axios.get(`${API_URL}/packet_timeline`),
        axios.get(`${API_URL}/protocol_summary_chart`),
      ]);
      setPackets(p1.data);
      setTimeline(p2.data);
      setProtocolChart(p3.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={`dashboard ${darkMode ? "dark" : ""}`}>
      <div className="header">
        <h1>📡 Packet Analyzer Dashboard</h1>
        <div>
          <button className="start">Start Sniffing</button>
          <button className="stop">Stop Sniffing</button>
          <button className="darkmode" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
          </button>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-around", marginTop: "20px" }}>
        <div style={{ width: "45%" }}>
          <h3>📊 Protocol Distribution</h3>
          <Pie
            data={{
              labels: protocolChart.labels,
              datasets: [{ data: protocolChart.counts, backgroundColor: ["#007bff","#ffc107","#28a745","#dc3545"] }],
            }}
          />
        </div>
        <div style={{ width: "45%" }}>
          <h3>📈 Packet Timeline</h3>
          <Line
            data={{
              labels: timeline.times,
              datasets: [{ label: "Packets", data: timeline.counts, borderColor: "#007bff", fill: false }],
            }}
          />
        </div>
      </div>

      <h3 style={{ marginTop: "30px" }}>📋 Captured Packets</h3>
      <table border="1" cellPadding="5" width="100%">
        <thead style={{ background: "#007bff", color: "white" }}>
          <tr>
            <th>ID</th><th>Source IP</th><th>Dest IP</th><th>Protocol</th><th>Summary</th><th>Time</th>
          </tr>
        </thead>
        <tbody>
          {packets.map(p => (
            <tr key={p.id}>
              <td>{p.id}</td><td>{p.src_ip}</td><td>{p.dest_ip}</td><td>{p.protocol}</td><td>{p.summary}</td><td>{p.time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
