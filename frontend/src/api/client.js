// Centralized API configuration for the Construction Intelligence Hub frontend.
//
// Every component previously hardcoded "http://127.0.0.1:8000" inline. That
// still works for local development, but this file gives a single place to
// change it (e.g. for a deployed backend) via a Vite env var, and a small
// fetch wrapper that times out instead of hanging forever when the backend
// is unreachable — which is common the first time someone runs this project
// and hasn't started the backend yet.

export const API_BASE_URL =
  (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_BASE_URL) ||
  "http://127.0.0.1:8000";

const DEFAULT_TIMEOUT_MS = 10000;

/**
 * Fetch a path relative to API_BASE_URL, aborting after `timeoutMs`.
 * Throws a normal Error (with `.isNetworkError = true`) if the backend
 * can't be reached at all, so callers can distinguish "backend is down"
 * from "backend returned a 4xx/5xx".
 */
export async function apiFetch(path, options = {}) {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, ...fetchOptions } = options;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      signal: controller.signal,
    });
    return response;
  } catch (err) {
    const networkError = new Error(
      err.name === "AbortError"
        ? `Request to ${path} timed out after ${timeoutMs}ms. Is the backend running at ${API_BASE_URL}?`
        : `Could not reach the backend at ${API_BASE_URL}${path}. Is it running?`
    );
    networkError.isNetworkError = true;
    networkError.cause = err;
    throw networkError;
  } finally {
    clearTimeout(timer);
  }
}

/** Convenience wrapper: apiFetch + JSON parse + non-2xx -> throw. */
export async function apiFetchJson(path, options = {}) {
  const res = await apiFetch(path, options);
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = body.detail || body.message || "";
    } catch {
      /* response wasn't JSON; ignore */
    }
    const err = new Error(detail || `Request failed (${res.status})`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}
