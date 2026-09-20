import React, { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from "lucide-react";

const ToastContext = createContext(null);

const ICONS = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const AUTO_DISMISS_MS = 4500;

/**
 * Wrap the app in <ToastProvider> once (done in main.jsx). Any component can
 * then call `const { showToast } = useToast()` and
 * `showToast("Alert resolved", "success")` instead of relying on a browser
 * alert() or a console.log that the user never sees.
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const timers = useRef({});

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    if (timers.current[id]) {
      clearTimeout(timers.current[id]);
      delete timers.current[id];
    }
  }, []);

  const showToast = useCallback(
    (message, type = "info", { duration = AUTO_DISMISS_MS } = {}) => {
      const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      setToasts((prev) => [...prev, { id, message, type }]);
      if (duration > 0) {
        timers.current[id] = setTimeout(() => dismiss(id), duration);
      }
      return id;
    },
    [dismiss]
  );

  const value = useMemo(() => ({ showToast, dismiss }), [showToast, dismiss]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-stack-ci" role="status" aria-live="polite">
        {toasts.map((t) => {
          const Icon = ICONS[t.type] || Info;
          return (
            <div key={t.id} className={`toast-ci toast-ci-${t.type}`}>
              <Icon size={18} className="toast-ci-icon" />
              <span className="toast-ci-message">{t.message}</span>
              <button
                type="button"
                className="toast-ci-close"
                aria-label="Dismiss notification"
                onClick={() => dismiss(t.id)}
              >
                <X size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

/** Access `{ showToast, dismiss }` from any component under <ToastProvider>. */
export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    // Fail soft rather than crashing the app if a component is rendered
    // outside the provider (e.g. in isolated tests).
    return { showToast: () => {}, dismiss: () => {} };
  }
  return ctx;
}
