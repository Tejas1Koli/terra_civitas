import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Card, Form, Input, Button, Typography, message } from "antd";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../providers/apiClient";
import { useState } from "react";

export const LoginPage = ({ onLoginSuccess }: { onLoginSuccess?: () => void }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const response = await apiClient.post("/auth/login", values);
      const { token, role, username } = response.data;
      
      // Store in localStorage
      localStorage.setItem("cctv_token", token);
      localStorage.setItem("cctv_role", role);
      localStorage.setItem("cctv_username", username);
      
      message.success("Login successful!");
      
      // Call callback if provided
      if (onLoginSuccess) {
        onLoginSuccess();
      }
      
      // Navigate after callback
      setTimeout(() => {
        navigate("/");
      }, 100);
    } catch (error: any) {
      message.error(error?.response?.data?.detail ?? "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <Card title="CCTV Analytics Login" bordered={false} className="login-card">
        <Typography.Paragraph type="secondary">
          Use admin/admin123 to sign in on a fresh environment.
        </Typography.Paragraph>
        <Form layout="vertical" onFinish={onFinish} requiredMark={false}>
          <Form.Item name="username" label="Username" rules={[{ required: true, message: "Username is required" }]}> 
            <Input prefix={<UserOutlined />} placeholder="admin" size="large" />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true, message: "Password is required" }]}> 
            <Input.Password prefix={<LockOutlined />} placeholder="••••••" size="large" />
          </Form.Item>
          <Button type="primary" htmlType="submit" size="large" block loading={loading}>
            Sign in
          </Button>
        </Form>
      </Card>
    </div>
  );
};
