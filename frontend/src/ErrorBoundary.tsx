import React from "react";
import { Result, Button } from "antd";

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "50px", textAlign: "center" }}>
          <Result
            status="500"
            title="Application Error"
            subTitle={this.state.error?.message || "Unknown error occurred"}
            extra={
              <Button type="primary" onClick={() => window.location.href = "/"}>
                Reload
              </Button>
            }
          />
        </div>
      );
    }

    return this.props.children;
  }
}
