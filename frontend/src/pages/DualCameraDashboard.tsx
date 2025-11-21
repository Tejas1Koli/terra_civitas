import { Col, Row, Space } from "antd";
import { useState } from "react";
import { SidebarSettings } from "../components/SidebarSettings";
import { DualVideoCard } from "../components/DualVideoCard";
import { DualAlertsPanel } from "../components/DualAlertsPanel";

export const DualCameraDashboard = () => {
  const handleVideoToggle = (cameraId: number, active: boolean) => {
    console.log(`Camera ${cameraId} is now ${active ? "running" : "stopped"}`);
  };

  return (
    <Row gutter={24} wrap>
      <Col xs={24} md={8} lg={6}>
        <SidebarSettings />
      </Col>
      <Col xs={24} md={16} lg={18}>
        <Space direction="vertical" size={24} style={{ width: "100%" }}>
          <DualVideoCard onToggle={handleVideoToggle} />
          <DualAlertsPanel />
        </Space>
      </Col>
    </Row>
  );
};
