import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import ErrorBoundary from "./components/ErrorBoundary";
import { ToastProvider } from "./context/ToastContext";

import "bootstrap/dist/css/bootstrap.min.css";
// NOTE: index.css defines every design-token CSS variable used across the
// app (--bg-app, --text-primary, the Outfit font, etc.). It must load
// AFTER bootstrap's reset (so our body/font rules win) and BEFORE App.css
// (so App.css's component styles can reference the variables it defines).
import "./index.css";
import "./App.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ErrorBoundary>
      <ToastProvider>
        <App />
      </ToastProvider>
    </ErrorBoundary>
  </React.StrictMode>
);