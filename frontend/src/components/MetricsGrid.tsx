import { Card, Col, Progress, Row, Statistic } from "antd";

interface Props {
  frameCount?: number;
  crimeCount?: number;
  fps?: number;
  latestThreat?: number;
  latestConfidence?: number;
}

export const MetricsGrid = ({ frameCount = 0, crimeCount = 0, fps = 0, latestThreat = 0, latestConfidence = 0 }: Props) => (
  <Row gutter={12} className="metrics-grid">
    <Col xs={12} md={6}>
      <Card bordered={false}>
        <Statistic title="Frames" value={frameCount} suffix="frames" />
      </Card>
    </Col>
    <Col xs={12} md={6}>
      <Card bordered={false}>
        <Statistic title="Crimes Detected" value={crimeCount} suffix="events" />
      </Card>
    </Col>
    <Col xs={12} md={6}>
      <Card bordered={false}>
        <Statistic title="Threat" value={(latestThreat * 100).toFixed(1)} suffix="%" />
        <Progress percent={Math.round(latestThreat * 100)} steps={6} strokeColor="#f5222d" showInfo={false} />
      </Card>
    </Col>
    <Col xs={12} md={6}>
      <Card bordered={false}>
        <Statistic title="Confidence" value={(latestConfidence * 100).toFixed(1)} suffix="%" />
        <Progress percent={Math.round(latestConfidence * 100)} steps={6} strokeColor="#52c41a" showInfo={false} />
      </Card>
    </Col>
    <Col span={24}>
      <Card bordered={false}>
        <Statistic title="Live FPS" value={fps.toFixed(2)} suffix="fps" />
      </Card>
    </Col>
  </Row>
);
