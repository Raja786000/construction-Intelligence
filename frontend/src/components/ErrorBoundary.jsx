import React from "react";
import { AlertOctagon, RotateCcw } from "lucide-react";

/**
 * Catches render-time errors anywhere below it in the tree and shows a
 * themed fallback instead of an unstyled white screen. This is a class
 * component because React error boundaries currently require one — there
 * is no hooks equivalent.
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // In a production build this is where you'd forward to an error-tracking
    // service. Logging to console keeps this dependency-free.
    console.error("Unhandled UI error caught by ErrorBoundary:", error, info);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--bg-app, #0b1120)",
          padding: "24px",
        }}
      >
        <div className="ci-card" style={{ maxWidth: "460px", textAlign: "center" }}>
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "14px",
              background: "rgba(239, 68, 68, 0.15)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "18px",
            }}
          >
            <AlertOctagon size={28} color="#f87171" />
          </div>
          <h2 style={{ color: "#fff", fontSize: "1.25rem", marginBottom: "8px" }}>
            Something went wrong
          </h2>
          <p style={{ color: "var(--text-secondary, #94a3b8)", fontSize: "0.9rem", marginBottom: "22px" }}>
            The interface hit an unexpected error and couldn't continue rendering this
            screen. Reloading usually fixes it; if it keeps happening, check the browser
            console for details.
          </p>
          <button className="btn-primary-ci" style={{ margin: "0 auto" }} onClick={this.handleReload}>
            <RotateCcw size={16} /> Reload the app
          </button>
        </div>
      </div>
    );
  }
}
