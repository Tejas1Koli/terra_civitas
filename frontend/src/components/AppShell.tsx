import { Layout, Menu, Typography, Space, Button } from "antd";
import { VideoCameraOutlined, BellOutlined, CheckCircleOutlined } from "@ant-design/icons";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";

const items = [
  { key: "dashboard", icon: <VideoCameraOutlined />, label: <Link to="/">Single Camera</Link> },
  { key: "dual", icon: <VideoCameraOutlined />, label: <Link to="/dual">Dual Cameras</Link> },
  { key: "alerts", icon: <BellOutlined />, label: <Link to="/alerts">Alerts</Link> },
  { key: "verified", icon: <CheckCircleOutlined />, label: <Link to="/verified">Verified</Link> },
];

export const AppShell = ({ onLogout }: { onLogout?: () => void }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  
  const getSelectedKey = () => {
    if (location.pathname === "/dual") return "dual";
    if (location.pathname.startsWith("/alerts")) return "alerts";
    if (location.pathname.startsWith("/verified")) return "verified";
    return "dashboard";
  };

  const username = localStorage.getItem("cctv_username") || "User";

  const handleLogout = () => {
    setIsLoggingOut(true);
    localStorage.removeItem("cctv_token");
    localStorage.removeItem("cctv_role");
    localStorage.removeItem("cctv_username");
    
    // Call parent callback
    if (onLogout) {
      onLogout();
    }
    
    setTimeout(() => {
      navigate("/login", { replace: true });
    }, 300);
  };

  return (
    <Layout className="app-shell">
      <Layout.Sider width={240} theme="dark" collapsible>
        <div className="logo">CCTV AI</div>
        <Menu theme="dark" mode="inline" items={items} selectedKeys={[getSelectedKey()]} />
      </Layout.Sider>
      <Layout>
        <Layout.Header className="app-header">
          <Typography.Title level={4}>CCTV Crime Detection System</Typography.Title>
          <Space align="center">
            <Typography.Text type="secondary">{username}</Typography.Text>
            <Button onClick={handleLogout} loading={isLoggingOut}>
              Logout
            </Button>
          </Space>
        </Layout.Header>
        <Layout.Content className="app-content">
          <Outlet />
        </Layout.Content>
      </Layout>
    </Layout>
  );
};
