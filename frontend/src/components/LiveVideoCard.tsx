import { Card, Typography, Space, Tag, Skeleton, Button } from "antd";
import { PlayCircleOutlined, PauseCircleOutlined } from "@ant-design/icons";

interface Props {
  frameSrc?: string;
  running: boolean;
  onToggle?: (next: boolean) => void;
}

export const LiveVideoCard = ({ frameSrc, running, onToggle }: Props) => (
  <Card className="live-video-card" bordered={false} bodyStyle={{ padding: 0 }}>
    <div className="live-video-header">
      <div>
        <Typography.Title level={3}>CCTV Crime Detection System - Analytics Dashboard</Typography.Title>
        <Typography.Text type="secondary">
          Real-time surveillance with confidence tracking, performance metrics, and threat analysis
        </Typography.Text>
      </div>
      <Space>
        <Tag color={running ? "green" : "red"}>{running ? "Running" : "Offline"}</Tag>
        <Button
          icon={running ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
          type="primary"
          onClick={() => onToggle?.(!running)}
        >
          {running ? "Stop" : "Start"} Detection
        </Button>
      </Space>
    </div>
    <div className="live-video-body">
      <Typography.Title level={4}>Live Webcam Detection</Typography.Title>
      <Typography.Text type="secondary">Video Feed</Typography.Text>
      <div className="video-frame">
        {frameSrc ? <img src={frameSrc} alt="Live feed" /> : <Skeleton.Image active style={{ width: "100%", height: 360 }} />}
      </div>
      <Typography.Text className="video-footer">
        📹 CCTV Crime Detection System v2.0 · GPU: Metal · Status: {running ? "✅ Running" : "⛔ Stopped"}
      </Typography.Text>
    </div>
  </Card>
);
