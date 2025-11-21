import { useState } from "react";
import type { CheckboxChangeEvent } from "antd/es/checkbox";
import type { RadioChangeEvent } from "antd/es/radio";
import type { SliderSingleProps } from "antd/es/slider";
import { Card, Divider, Radio, Slider, Typography, Space, Checkbox, Switch } from "antd";
import { apiClient } from "../providers/apiClient";

const modes = [
  { label: "📹 Live Webcam", value: "live" },
  { label: "📼 Video Upload", value: "upload" },
  { label: "📊 Analytics Dashboard", value: "analytics" },
];

export const SidebarSettings = () => {
  const [mode, setMode] = useState("live");
  const [threshold, setThreshold] = useState(0.35);
  const [sensitivity, setSensitivity] = useState(0.85);
  const [options, setOptions] = useState({ motion: true, clustering: false, weapons: true });
  const [autoStart, setAutoStart] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const pushSettings = async (payload: Record<string, unknown>) => {
    setIsSubmitting(true);
    try {
      await apiClient.post("/live/settings", {
        fps_target: 15,
        crime_threshold: threshold,
        show_boxes: options.motion,
        show_weapons: options.weapons,
        ...payload,
      });
    } catch (error) {
      console.error("Failed to update settings:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOptionChange = (key: keyof typeof options, checked: boolean) => {
    const next = { ...options, [key]: checked };
    setOptions(next);
    pushSettings({ show_boxes: next.motion, show_weapons: next.weapons });
  };

  return (
    <Card bordered={false} className="sidebar-card">
      <Typography.Title level={5}>Settings</Typography.Title>
      <Typography.Text type="secondary">Detection Mode</Typography.Text>
      <Radio.Group
        options={modes}
        value={mode}
        onChange={(event: RadioChangeEvent) => setMode(event.target.value)}
        optionType="button"
        className="mode-group"
      />

      <Divider />
      <Typography.Text strong>Threat Threshold</Typography.Text>
      <Slider
        value={threshold}
        step={0.05}
        min={0}
        max={1}
  tooltip={{ formatter: (value?: number) => (value ? value.toFixed(2) : undefined) }}
  onChange={(value: number) => setThreshold(value)}
  onAfterChange={(value: number) => pushSettings({ crime_threshold: value })}
      />
      <Typography.Text type="secondary">Current: {threshold.toFixed(2)} (0-1 scale)</Typography.Text>

      <Divider />
      <Typography.Text strong>Detection Options</Typography.Text>
      <Space direction="vertical">
  <Checkbox checked={options.motion} onChange={(e: CheckboxChangeEvent) => handleOptionChange("motion", e.target.checked)}>
          🔴 Show Motion Detection
        </Checkbox>
  <Checkbox checked={options.clustering} onChange={(e: CheckboxChangeEvent) => handleOptionChange("clustering", e.target.checked)}>
          👥 Show Clustering
        </Checkbox>
  <Checkbox checked={options.weapons} onChange={(e: CheckboxChangeEvent) => handleOptionChange("weapons", e.target.checked)}>
          🗡️ Show Weapons
        </Checkbox>
      </Space>

      <Divider />
      <Typography.Text strong>Sensitivity</Typography.Text>
  <Slider value={sensitivity} min={0} max={1} step={0.01} onChange={(value: number) => setSensitivity(value)} />
      <Typography.Text type="secondary">Motion Sensitivity: {sensitivity.toFixed(2)}</Typography.Text>

      <Divider />
      <Space align="center">
        <Typography.Text strong>Auto start detection</Typography.Text>
        <Switch
          checked={autoStart}
          loading={isSubmitting}
          onChange={async (checked: boolean) => {
            setAutoStart(checked);
            try {
              await apiClient.post("/live/control", { active: checked });
            } catch (error) {
              console.error("Failed to toggle detection:", error);
            }
          }}
        />
      </Space>
    </Card>
  );
};
