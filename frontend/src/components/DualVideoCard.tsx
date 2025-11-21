import { Card, Row, Col, Space, Tag, Button, Skeleton, Typography } from "antd";
import { PlayCircleOutlined, PauseCircleOutlined } from "@ant-design/icons";
import { useState, useEffect } from "react";
import { apiClient } from "../providers/apiClient";

interface CameraStats {
  frame_count: number;
  crime_count: number;
  fps: number;
  running: boolean;
  source_type: string;
  latest_results?: {
    smoothed_score: number;
    confidence: number;
    weapons_count: number;
  };
}

interface Props {
  onToggle?: (cameraId: number, active: boolean) => void;
}

export const DualVideoCard = ({ onToggle }: Props) => {
  const [frame1, setFrame1] = useState<string>("");
  const [frame2, setFrame2] = useState<string>("");
  const [toggleLoading, setToggleLoading] = useState<Record<number, boolean>>({
    1: false,
    2: false,
  });
  const [stats1, setStats1] = useState<CameraStats>({
    frame_count: 0,
    crime_count: 0,
    fps: 0,
    running: false,
    source_type: "unknown",
  });
  const [stats2, setStats2] = useState<CameraStats>({
    frame_count: 0,
    crime_count: 0,
    fps: 0,
    running: false,
    source_type: "unknown",
  });

  // Fetch stats from both cameras
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await apiClient.get("/live/dual/stats");
        setStats1(res.data.camera_1);
        setStats2(res.data.camera_2);
      } catch (error) {
        console.error("Error fetching dual stats:", error);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Fetch frame from camera 1
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await apiClient.get("/live/dual/frame/1");
        setFrame1(res.data?.frame || "");
      } catch (error) {
        console.error("Error fetching frame 1:", error);
      }
    }, 33);
    return () => clearInterval(interval);
  }, []);

  // Fetch frame from camera 2
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await apiClient.get("/live/dual/frame/2");
        setFrame2(res.data?.frame || "");
      } catch (error) {
        console.error("Error fetching frame 2:", error);
      }
    }, 33);
    return () => clearInterval(interval);
  }, []);

  const handleToggle = async (cameraId: number, active: boolean) => {
    setToggleLoading((prev) => ({ ...prev, [cameraId]: true }));
    if (cameraId === 1) {
      setStats1((prev) => ({ ...prev, running: active }));
    } else {
      setStats2((prev) => ({ ...prev, running: active }));
    }

    try {
      await apiClient.post(`/live/dual/control/${cameraId}`, { active });
      const res = await apiClient.get("/live/dual/stats");
      setStats1(res.data.camera_1);
      setStats2(res.data.camera_2);
      onToggle?.(cameraId, active);
    } catch (error) {
      console.error(`Error toggling camera ${cameraId}:`, error);
      // revert optimistic change
      if (cameraId === 1) {
        setStats1((prev) => ({ ...prev, running: !active }));
      } else {
        setStats2((prev) => ({ ...prev, running: !active }));
      }
    } finally {
      setToggleLoading((prev) => ({ ...prev, [cameraId]: false }));
    }
  };

  const CameraView = ({
    cameraId,
    frame,
    stats,
  }: {
    cameraId: number;
    frame: string;
    stats: CameraStats;
  }) => (
    <Card className="live-video-card" bordered={false} style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ marginBottom: 16 }}>
        <Space style={{ width: "100%", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <Typography.Title level={4} style={{ margin: 0 }}>
              Camera {cameraId}
            </Typography.Title>
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {stats.source_type.toUpperCase()} · {stats.fps.toFixed(1)} FPS · Frame {stats.frame_count}
            </Typography.Text>
          </div>
          <Space direction="vertical" align="end" style={{ gap: 8 }}>
            <Tag color={stats.running ? "green" : "red"}>
              {stats.running ? "Running" : "Offline"}
            </Tag>
            <Button
              icon={stats.running ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
              type="primary"
              size="small"
              onClick={() => handleToggle(cameraId, !stats.running)}
              loading={toggleLoading[cameraId]}
            >
              {stats.running ? "Stop" : "Start"}
            </Button>
          </Space>
        </Space>
      </div>

      <div style={{ marginBottom: 12, flex: 1, display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
        <div 
          className="video-frame" 
          style={{ 
            width: "100%", 
            height: "100%",
            minHeight: 300,
            backgroundColor: "#000",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
        >
          {frame ? (
            <img 
              src={frame} 
              alt={`Camera ${cameraId} feed`} 
              style={{ 
                maxWidth: "100%", 
                maxHeight: "100%",
                objectFit: "contain"
              }} 
            />
          ) : (
            <Skeleton.Image active style={{ width: "100%", height: 300 }} />
          )}
        </div>
      </div>

      <div
        style={{
          padding: "12px 0",
          borderTop: "1px solid #f0f0f0",
          display: "flex",
          justifyContent: "space-between",
          fontSize: 12,
        }}
      >
        <span>🎯 Detections: {stats.crime_count}</span>
        <span>
          📊 Confidence:{" "}
          {((stats.latest_results?.confidence ?? 0) * 100).toFixed(1)}%
        </span>
        <span>
          ⚠️ Threat: {((stats.latest_results?.smoothed_score ?? 0) * 100).toFixed(1)}%
        </span>
      </div>
    </Card>
  );

  return (
    <Card className="dual-video-card" bordered={false}>
      <div style={{ marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          Dual CCTV Camera Streams
        </Typography.Title>
        <Typography.Text type="secondary">
          Real-time monitoring from 2 camera feeds with independent alerts and verification
        </Typography.Text>
      </div>

      <Row gutter={16}>
        <Col xs={24} sm={24} md={12}>
          <CameraView cameraId={1} frame={frame1} stats={stats1} />
        </Col>
        <Col xs={24} sm={24} md={12}>
          <CameraView cameraId={2} frame={frame2} stats={stats2} />
        </Col>
      </Row>
    </Card>
  );
};
