# Frontend UI/UX Update

This document summarizes the UI/UX work done on `frontend/` (the Vite +
React 19 app served at `localhost:5173`). Scope was the active, documented
app described in `README.md` / `HOW_TO_RUN.md` — the `milestone 3`,
`milestone 4`, `Quality_inspection_agent`, and `construction_risk_platform`
folders are earlier snapshots and were left untouched.

## Bug fixed

- **`index.css` was never imported.** `main.jsx` imported Bootstrap's CSS
  and `App.css`, but not `index.css` — the file that defines every color
  variable (`--bg-app`, `--text-primary`, `--primary`, etc.), the Outfit
  font, and the custom scrollbar. Confirmed by diffing the built CSS
  bundle: the custom `:root` block was completely absent. Every component
  referencing `var(--bg-card)`, `var(--text-secondary)`, etc. was silently
  falling back to invalid/initial values. This is now imported in the
  correct order (`bootstrap.min.css` → `index.css` → `App.css`) in
  `src/main.jsx`.
- **Demo login credentials didn't match the docs.** The "Safety Officer"
  and "Project Manager" quick-demo buttons in `LoginModal.jsx` filled in
  `safety.officer@construction.ai` / `pm.verma@construction.ai`, but
  `README.md` and `HOW_TO_RUN.md` document `safety@construction.ai` /
  `manager@construction.ai`. Aligned the code to the documented
  credentials.
- **`DashboardOverview`'s `loading` state was tracked but never rendered.**
  The KPI grid popped in abruptly with no loading indication. It now shows
  a skeleton grid (`components/Skeleton.jsx`) while the first fetch is in
  flight.
- **Generic page title.** `<title>frontend</title>` → `Construction
  Intelligence Hub`, plus a meta description and theme-color.

## New reusable pieces

| File | Purpose |
|---|---|
| `src/context/ToastContext.jsx` | App-wide toast notifications (`useToast().showToast(msg, "success"\|"error"\|"warning"\|"info")`) instead of silent `console.log`/`console.error` calls the user never sees. |
| `src/components/ErrorBoundary.jsx` | Catches render-time errors and shows a themed recovery screen instead of a blank white page. Wraps `<App />` in `main.jsx`. |
| `src/components/EmptyState.jsx` | Consistent "nothing here yet" placeholder for empty lists/tables, with an optional call-to-action button. |
| `src/components/Skeleton.jsx` | `SkeletonBlock`, `KpiSkeletonGrid`, `TableSkeletonRows` — shimmering loading placeholders. |
| `src/api/client.js` | `API_BASE_URL` (reads `VITE_API_BASE_URL`, falls back to `http://127.0.0.1:8000`) and `apiFetch()` (adds a request timeout + a clear "can't reach the backend" error instead of a hung request). |

## Feature additions

- **Light/dark theme toggle** — sun/moon button in the sidebar footer.
  Persisted to `localStorage`, applied via `<html data-theme="light">`,
  using the same CSS variable names every component already reads, so no
  component needed to change to support it. Light palette added in
  `index.css`.
- **Mobile navigation drawer.** Below 560px, the sidebar becomes a real
  off-canvas drawer (with a backdrop) opened by a hamburger button in the
  header, instead of the previous icon-only rail with no visible labels.
  The existing 900px icon-rail breakpoint (tablet) is unchanged.
- **Backend-unreachable banner.** If every initial API call fails to
  connect at all (not just returns a 4xx/5xx), a dismissible banner
  appears with a "Retry" button — this is the single most likely first
  failure mode for anyone running this project for the first time without
  the backend started yet.
- **Toast feedback wired into:** login (success), sign-out, `AlertsCenter`
  (resolve/delete/dispatch — success and failure), and connection retry.
- Password show/hide toggle on the login form.
- A subtle fade-in transition when switching between sidebar tabs.
- Visible keyboard-focus outlines on interactive elements (accessibility).
- `prefers-reduced-motion` respected for all custom transitions/animations.

## Centralized API base URL

Every component previously hardcoded `"http://127.0.0.1:8000"` inline
(9 files, ~28 occurrences). These now import `API_BASE_URL` from
`src/api/client.js`, so pointing the frontend at a deployed backend is a
one-line change (or a `VITE_API_BASE_URL` env var) instead of a find-and-
replace across the codebase. `LoginModal` and `AlertsCenter` additionally
use the `apiFetch()` wrapper for its timeout + clearer error message;
the file-upload/video/webcam endpoints (`SafetySurveillance`,
`ReportConsolidator`'s PDF link, `LiveMonitoring`) keep using plain
`fetch()` with the new constant, since those requests can legitimately
run longer than a short timeout would allow.

## Not changed in this pass

`ProjectManagement`, `WorkerManagement`, `SafetySurveillance`,
`QualityMonitoring`, `RiskPrediction`, `WeatherWidget`, `ReportConsolidator`,
`ProjectMonitoring`, and `LiveMonitoring` all inherit the theme fix, the
toast system, the responsive layout, and the centralized API base URL for
free, but their own create/update/delete actions still report
success/failure via `console.log`/`console.error` only rather than the new
toast pattern, and their empty-list states aren't using `EmptyState` yet.
Wiring those in follows the exact same pattern used in `AlertsCenter.jsx`
(import `useToast`, call `showToast(...)` in each `catch` block and after
each successful mutation) if you'd like to extend it further.

## Verification performed

- `npm run build` succeeds (Vite production build, no errors).
- `npx oxlint` reports 0 errors (43 pre-existing warnings, all unrelated to
  this change — unused lucide-react icon imports and `react-hooks/exhaustive-deps`
  notices that predate this update).
