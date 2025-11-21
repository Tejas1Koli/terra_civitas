import { Col, Row, Space, notification } from "antd";
import { useState, useEffect } from "react";
import { SidebarSettings } from "../components/SidebarSettings";
import { LiveVideoCard } from "../components/LiveVideoCard";
import { MetricsGrid } from "../components/MetricsGrid";
import { AlertsPanel } from "../components/AlertsPanel";
import { apiClient } from "../providers/apiClient";

export const DashboardPage = () => {
  const [stats, setStats] = useState<any>({});
  const [frame, setFrame] = useState<string>("");
  const [alerts, setAlerts] = useState<any[]>([]);

  // Fetch stats every 1s
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await apiClient.get("/live/stats");
        setStats(res.data);
      } catch (error) {
        console.error("Error fetching stats:", error);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Fetch frame every 33ms (30fps)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await apiClient.get("/live/frame");
        setFrame(res.data?.frame || "");
      } catch (error) {
        console.error("Error fetching frame:", error);
      }
    }, 33);
    return () => clearInterval(interval);
  }, []);

  // Fetch live alerts every 2s (from persistent storage, not temporary queue)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await apiClient.get("/alerts/recent?limit=10");
        // Handle both array and object response
        const alertsList = Array.isArray(res.data) ? res.data : res.data?.data || res.data?.alerts || [];
        
        // Transform alerts to match AlertsPanel expectations
        const transformed = alertsList.map((alert: any) => ({
          id: alert.id || alert.alert_id,
          alert_id: alert.alert_id,
          threat_score: alert.threat_score || 0,
          confidence: alert.confidence || 0,
          weapons_count: alert.detection_details?.weapons_detected || alert.weapons?.length || 0,
          timestamp: alert.timestamp || new Date().toISOString(),
        }));
        
        setAlerts(transformed);
      } catch (error) {
        console.error("Error fetching alerts:", error);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleToggle = async (active: boolean) => {
    try {
      const res = await apiClient.post("/live/control", { active });
      notification.success({
        message: active ? "Detection Started" : "Detection Stopped",
        description: `Detection is now ${active ? "running" : "stopped"}`,
      });
      // Refresh stats
      const statsRes = await apiClient.get("/live/stats");
      setStats(statsRes.data);
    } catch (error: any) {
      notification.error({
        message: "Error",
        description: error?.response?.data?.detail || "Failed to toggle detection",
      });
    }
  };

  return (
    <Row gutter={24} wrap>
      <Col xs={24} md={8} lg={6}>
        <SidebarSettings />
      </Col>
      <Col xs={24} md={16} lg={18}>
        <Space direction="vertical" size={24} style={{ width: "100%" }}>
          <LiveVideoCard 
            frameSrc={frame} 
            running={stats.running ?? false} 
            onToggle={handleToggle} 
          />
          <MetricsGrid
            frameCount={stats.frame_count || 0}
            crimeCount={stats.crime_count || 0}
            fps={stats.fps || 0}
            latestThreat={stats.latest_results?.smoothed_score ?? 0}
            latestConfidence={stats.latest_results?.confidence ?? 0}
          />
          <AlertsPanel alerts={alerts} />
        </Space>
      </Col>
    </Row>
  );
};
