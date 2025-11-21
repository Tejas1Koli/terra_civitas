import { Card, Collapse, Button, Space, Tag, Typography, Empty, message } from "antd";
import { useState } from "react";
import { apiClient } from "../providers/apiClient";

type AlertItem = {
  id: string;
  alert_id?: string;
  threat_score: number;
  confidence: number;
  weapons_count: number;
  timestamp: string;
};

interface Props {
  alerts: AlertItem[];
}

export const AlertsPanel = ({ alerts }: Props) => {
  const [loading, setLoading] = useState(false);
  const username = localStorage.getItem("cctv_username") || "admin";

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

  if (!alerts.length) {
    return (
      <Card bordered={false} className="alerts-card">
        <Typography.Title level={4}>Live Alerts</Typography.Title>
        <Empty description="No live alerts" />
      </Card>
    );
  }

  return (
    <Card bordered={false} className="alerts-card">
      <Typography.Title level={4}>Live Alerts</Typography.Title>
      <Collapse accordion expandIconPosition="end">
        {alerts.map((alert) => {
          const alertId = alert.id || alert.alert_id || "unknown";
          return (
            <Collapse.Panel
              header={`${alertId} · Threat ${(alert.threat_score * 100).toFixed(1)}%`}
              key={alertId}
              extra={<Tag color="red">Weapons {alert.weapons_count}</Tag>}
            >
              <Space direction="vertical" size="middle">
                <Typography.Text>
                  Confidence: {(alert.confidence * 100).toFixed(1)}% · Detected at {alert.timestamp}
                </Typography.Text>
                <Space>
                  <Button type="primary" loading={loading} onClick={() => handleVerify(alertId, 1)}>
                    ✅ Verify Alert
                  </Button>
                  <Button danger loading={loading} onClick={() => handleVerify(alertId, 0)}>
                    ❌ Reject Alert
                  </Button>
                </Space>
              </Space>
            </Collapse.Panel>
          );
        })}
      </Collapse>
    </Card>
  );
};
