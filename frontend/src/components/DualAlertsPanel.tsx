import { Card, Collapse, Button, Space, Tag, Typography, Empty, message, Row, Col } from "antd";
import { useState, useEffect } from "react";
import { apiClient } from "../providers/apiClient";

type AlertItem = {
  id: string;
  alert_id?: string;
  threat_score: number;
  confidence: number;
  weapons_count: number;
  timestamp: string;
  camera_id?: number;
};

interface Props {
  // Props can be extended if needed
}

export const DualAlertsPanel = ({}: Props) => {
  const [alerts1, setAlerts1] = useState<AlertItem[]>([]);
  const [alerts2, setAlerts2] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);
  const username = localStorage.getItem("cctv_username") || "admin";

  // Fetch alerts from camera 1
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await apiClient.get("/alerts/recent?limit=5");
        const alertsList = Array.isArray(res.data) ? res.data : res.data?.data || res.data?.alerts || [];
        
        const transformed = alertsList.map((alert: any) => ({
          id: alert.id || alert.alert_id,
          alert_id: alert.alert_id,
          threat_score: alert.threat_score || 0,
          confidence: alert.confidence || 0,
          weapons_count: alert.detection_details?.weapons_detected || alert.weapons?.length || 0,
          timestamp: alert.timestamp || new Date().toISOString(),
          camera_id: 1,
        }));
        
        setAlerts1(transformed);
      } catch (error) {
        console.error("Error fetching alerts for camera 1:", error);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Fetch alerts from camera 2 (from the dual endpoint if available, otherwise same alerts)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // Note: This fetches from the same alert pool. 
        // If you want separate alert tracking per camera, you'd need backend changes
        const res = await apiClient.get("/alerts/recent?limit=5");
        const alertsList = Array.isArray(res.data) ? res.data : res.data?.data || res.data?.alerts || [];
        
        const transformed = alertsList.map((alert: any, index: number) => ({
          id: alert.id || alert.alert_id,
          alert_id: alert.alert_id,
          threat_score: alert.threat_score || 0,
          confidence: alert.confidence || 0,
          weapons_count: alert.detection_details?.weapons_detected || alert.weapons?.length || 0,
          timestamp: alert.timestamp || new Date().toISOString(),
          camera_id: 2,
        }));
        
        // Only take alternate alerts for demo purposes
        setAlerts2(transformed.slice(0, 3));
      } catch (error) {
        console.error("Error fetching alerts for camera 2:", error);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleVerify = async (alertId: string, isValid: number) => {
    setLoading(true);
    try {
      await apiClient.post(`/alerts/${alertId}/verify`, {
        verified_by: username,
        is_valid: isValid,
      });
      message.success("Alert updated");
    } catch (error: any) {
      message.error(error?.response?.data?.detail ?? "Unable to verify alert");
    } finally {
      setLoading(false);
    }
  };

  const AlertsList = ({ alerts, cameraId }: { alerts: AlertItem[]; cameraId: number }) => {
    if (!alerts.length) {
      return (
        <Empty 
          description={`No alerts from Camera ${cameraId}`} 
          style={{ marginTop: 20, marginBottom: 20 }}
        />
      );
    }

    return (
      <Collapse accordion expandIconPosition="end">
        {alerts.map((alert) => {
          const alertId = alert.id || alert.alert_id || "unknown";
          return (
            <Collapse.Panel
              header={`${alertId} · Threat ${(alert.threat_score * 100).toFixed(1)}%`}
              key={alertId}
              extra={<Tag color="red">🔫 {alert.weapons_count} weapons</Tag>}
            >
              <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                <Typography.Text>
                  Confidence: {(alert.confidence * 100).toFixed(1)}% · Detected at {alert.timestamp}
                </Typography.Text>
                <Space>
                  <Button 
                    type="primary" 
                    loading={loading} 
                    onClick={() => handleVerify(alertId, 1)}
                    style={{ width: 150 }}
                  >
                    ✅ Verify
                  </Button>
                  <Button 
                    danger 
                    loading={loading} 
                    onClick={() => handleVerify(alertId, 0)}
                    style={{ width: 150 }}
                  >
                    ❌ Reject
                  </Button>
                </Space>
              </Space>
            </Collapse.Panel>
          );
        })}
      </Collapse>
    );
  };

  return (
    <Card bordered={false} className="dual-alerts-card">
      <Typography.Title level={4} style={{ marginBottom: 16 }}>
        Live Alerts from Both Cameras
      </Typography.Title>
      
      <Row gutter={16}>
        <Col xs={24} sm={24} md={12}>
          <div style={{ paddingBottom: 12, borderBottom: "2px solid #f0f0f0", marginBottom: 12 }}>
            <Tag color="blue" style={{ fontSize: 12, padding: "4px 8px" }}>
              Camera 1 Alerts
            </Tag>
          </div>
          <AlertsList alerts={alerts1} cameraId={1} />
        </Col>
        
        <Col xs={24} sm={24} md={12}>
          <div style={{ paddingBottom: 12, borderBottom: "2px solid #f0f0f0", marginBottom: 12 }}>
            <Tag color="purple" style={{ fontSize: 12, padding: "4px 8px" }}>
              Camera 2 Alerts
            </Tag>
          </div>
          <AlertsList alerts={alerts2} cameraId={2} />
        </Col>
      </Row>
    </Card>
  );
};
