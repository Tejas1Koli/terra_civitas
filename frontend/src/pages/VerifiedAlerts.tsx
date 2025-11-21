import { Table, Typography, Spin } from "antd";
import { useState, useEffect } from "react";
import { apiClient } from "../providers/apiClient";

export const VerifiedAlertsPage = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get("/alerts/verified");
        setAlerts(Array.isArray(response.data) ? response.data : response.data.data ?? []);
      } catch (error) {
        console.error("Failed to fetch verified alerts:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  return (
    <div className="table-page">
      <Typography.Title level={3}>Verified Alerts</Typography.Title>
      <Spin spinning={loading}>
        <Table
          loading={loading}
          dataSource={alerts}
          rowKey={(record: any) => record.id || record.alert_id}
          pagination={{ pageSize: 10 }}
          columns={[
            {
              title: "Alert ID",
              dataIndex: "alert_id",
            },
            {
              title: "Verified By",
              dataIndex: "verified_by",
            },
            {
              title: "Verified At",
              dataIndex: "verified_at",
            },
          ]}
        />
      </Spin>
    </div>
  );
};