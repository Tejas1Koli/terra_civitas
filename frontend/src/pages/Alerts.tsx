import { useState, useEffect } from "react";
import { Table, Tag, Typography } from "antd";
import { apiClient } from "../providers/apiClient";

export const AlertsPage = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get("/alerts/recent");
        setAlerts(res.data?.alerts || []);
      } catch (error) {
        console.error("Error fetching alerts:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  return (
    <div className="table-page">
      <Typography.Title level={3}>Recent Alerts</Typography.Title>
      <Table
        loading={loading}
        dataSource={alerts}
        rowKey={(record: any) => record.id || record.alert_id}
        pagination={{ pageSize: 10 }}
        columns={[
          {
            title: "Alert ID",
            dataIndex: "id",
            key: "id",
          },
          {
            title: "Threat",
            dataIndex: "threat_score",
            render: (value: number) => `${(value * 100).toFixed(1)}%`,
          },
          {
            title: "Confidence",
            dataIndex: "confidence",
            render: (value: number) => `${(value * 100).toFixed(1)}%`,
          },
          {
            title: "Weapons",
            dataIndex: "weapons_count",
            render: (value: number) => <Tag color={value ? "red" : "green"}>{value ?? 0}</Tag>,
          },
          {
            title: "Timestamp",
            dataIndex: "timestamp",
          },
        ]}
      />
    </div>
  );
};
