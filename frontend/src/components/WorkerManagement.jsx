import React, { useState, useEffect } from "react";
import {
  Users,
  Plus,
  Edit2,
  Trash2,
  ShieldCheck,
  ShieldAlert,
  Search,
  Check,
  X,
  Phone,
  Award,
  HardHat,
  Filter
} from "lucide-react";

export default function WorkerManagement() {
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterViolationOnly, setFilterViolationOnly] = useState(false);

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    worker_id: "W108",
    name: "Vikram Singh",
    assigned_task: "Brick work",
    helmet: "Yes",
    vest: "No",
    mobile: "+91 98111 22334",
    certification: "OSHA-10 Certified",
    project_id: "PROJ-METRO"
  });

  useEffect(() => {
    fetchWorkers();
  }, [filterViolationOnly]);

  const fetchWorkers = async () => {
    try {
      setLoading(true);
      const url = filterViolationOnly
        ? "http://127.0.0.1:8000/api/workers?ppe_violation_only=true"
        : "http://127.0.0.1:8000/api/workers";
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setWorkers(data);
      }
    } catch (err) {
      console.error("Error loading workers:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:8000/api/workers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setShowAddModal(false);
        fetchWorkers();
      }
    } catch (err) {
      console.error("Failed to add worker:", err);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!selectedWorker) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/workers/${selectedWorker.worker_id || selectedWorker._id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setShowEditModal(false);
        fetchWorkers();
      }
    } catch (err) {
      console.error("Failed to update worker:", err);
    }
  };

  const handleDelete = async (workerId) => {
    if (!window.confirm(`Are you sure you want to remove Worker ${workerId}?`)) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/workers/${workerId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        fetchWorkers();
      }
    } catch (err) {
      console.error("Failed to delete worker:", err);
    }
  };

  const handleTogglePPE = async (workerId, ppeType) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/workers/${workerId}/toggle-ppe?ppe_type=${ppeType}`, {
        method: "PATCH"
      });
      if (res.ok) {
        fetchWorkers();
      }
    } catch (err) {
      console.error("Failed to toggle PPE:", err);
    }
  };

  const openEdit = (w) => {
    setSelectedWorker(w);
    setFormData({
      worker_id: w.worker_id || w._id,
      name: w.name || "",
      assigned_task: w.assigned_task || "",
      helmet: w.helmet || "Yes",
      vest: w.vest || "Yes",
      mobile: w.mobile || "",
      certification: w.certification || "",
      project_id: w.project_id || "PROJ-METRO"
    });
    setShowEditModal(true);
  };

  const filteredWorkers = workers.filter((w) => {
    const s = searchTerm.toLowerCase();
    return (
      (w.name && w.name.toLowerCase().includes(s)) ||
      (w.worker_id && w.worker_id.toLowerCase().includes(s)) ||
      (w.assigned_task && w.assigned_task.toLowerCase().includes(s)) ||
      (w.certification && w.certification.toLowerCase().includes(s))
    );
  });

  const totalViolations = workers.filter((w) => w.helmet === "No" || w.vest === "No" || w.ppe_status === "VIOLATION").length;

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: "700", color: "#fff", margin: "0 0 4px 0" }}>
            Worker Management & Site PPE Compliance
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Track site personnel, assigned duties, and real-time Hardhat & Safety Vest compliance
          </p>
        </div>

        <button
          className="btn-primary-ci"
          onClick={() => {
            setFormData({
              worker_id: `W${100 + workers.length + 1}`,
              name: "",
              assigned_task: "Brick work",
              helmet: "Yes",
              vest: "No",
              mobile: "",
              certification: "Certified Construction Worker",
              project_id: "PROJ-METRO"
            });
            setShowAddModal(true);
          }}
        >
          <Plus size={18} /> Add Worker
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ position: "relative", width: "340px" }}>
          <Search size={18} style={{ position: "absolute", left: "14px", top: "12px", color: "var(--text-muted)" }} />
          <input
            type="text"
            className="form-control-ci"
            style={{ paddingLeft: "42px" }}
            placeholder="Search by worker name, task, or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            className={`btn-secondary-ci ${filterViolationOnly ? "active" : ""}`}
            style={{
              backgroundColor: filterViolationOnly ? "rgba(239, 68, 68, 0.2)" : "#334155",
              borderColor: filterViolationOnly ? "#ef4444" : "rgba(255, 255, 255, 0.1)",
              color: filterViolationOnly ? "#f87171" : "#f1f5f9"
            }}
            onClick={() => setFilterViolationOnly(!filterViolationOnly)}
          >
            <Filter size={16} /> Filter PPE Violations ({totalViolations})
          </button>
        </div>
      </div>

      {/* Workers Table */}
      <div className="ci-table-wrap">
        <table className="ci-table">
          <thead>
            <tr>
              <th>Worker ID</th>
              <th>Worker Name</th>
              <th>Assigned Task</th>
              <th style={{ textAlign: "center" }}>Helmet</th>
              <th style={{ textAlign: "center" }}>Safety Vest</th>
              <th>PPE Compliance</th>
              <th>Mobile No</th>
              <th>Certification</th>
              <th style={{ textAlign: "right" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredWorkers.map((w) => {
              const wId = w.worker_id || w._id;
              const hasHelmet = w.helmet === "Yes";
              const hasVest = w.vest === "Yes";
              const isViolation = !hasHelmet || !hasVest || w.ppe_status === "VIOLATION";

              return (
                <tr key={wId}>
                  <td>
                    <span style={{
                      fontFamily: "var(--font-mono)",
                      fontWeight: "700",
                      color: "#60a5fa",
                      padding: "3px 8px",
                      background: "rgba(59, 130, 246, 0.12)",
                      borderRadius: "6px"
                    }}>
                      {wId}
                    </span>
                  </td>
                  <td>
                    <strong style={{ color: "#fff", display: "block" }}>{w.name}</strong>
                    <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{w.project_id || "PROJ-METRO"}</span>
                  </td>
                  <td>
                    <span style={{ color: "#e2e8f0", fontWeight: "500" }}>{w.assigned_task}</span>
                  </td>
                  {/* Helmet Toggle Button */}
                  <td style={{ textAlign: "center" }}>
                    <button
                      title="Click to toggle Helmet status"
                      style={{
                        background: hasHelmet ? "rgba(16, 185, 129, 0.2)" : "rgba(239, 68, 68, 0.2)",
                        color: hasHelmet ? "#34d399" : "#f87171",
                        border: `1px solid ${hasHelmet ? "rgba(16, 185, 129, 0.4)" : "rgba(239, 68, 68, 0.4)"}`,
                        borderRadius: "8px",
                        padding: "4px 10px",
                        fontSize: "0.78rem",
                        fontWeight: "600",
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px"
                      }}
                      onClick={() => handleTogglePPE(wId, "helmet")}
                    >
                      {hasHelmet ? <Check size={13} /> : <X size={13} />}
                      {hasHelmet ? "Yes" : "No"}
                    </button>
                  </td>
                  {/* Vest Toggle Button */}
                  <td style={{ textAlign: "center" }}>
                    <button
                      title="Click to toggle Vest status"
                      style={{
                        background: hasVest ? "rgba(16, 185, 129, 0.2)" : "rgba(239, 68, 68, 0.2)",
                        color: hasVest ? "#34d399" : "#f87171",
                        border: `1px solid ${hasVest ? "rgba(16, 185, 129, 0.4)" : "rgba(239, 68, 68, 0.4)"}`,
                        borderRadius: "8px",
                        padding: "4px 10px",
                        fontSize: "0.78rem",
                        fontWeight: "600",
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px"
                      }}
                      onClick={() => handleTogglePPE(wId, "vest")}
                    >
                      {hasVest ? <Check size={13} /> : <X size={13} />}
                      {hasVest ? "Yes" : "No"}
                    </button>
                  </td>
                  <td>
                    <span className={`badge-pill ${isViolation ? "badge-danger" : "badge-success"}`}>
                      {isViolation ? <ShieldAlert size={12} /> : <ShieldCheck size={12} />}
                      {isViolation ? "VIOLATION" : "COMPLIANT"}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)", display: "inline-flex", alignItems: "center", gap: "4px" }}>
                      <Phone size={12} color="#94a3b8" /> {w.mobile || "—"}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: "0.82rem", color: "#cbd5e1", display: "inline-flex", alignItems: "center", gap: "4px" }}>
                      <Award size={12} color="#fbbf24" /> {w.certification || "General Labor"}
                    </span>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <div style={{ display: "inline-flex", gap: "6px" }}>
                      <button
                        title="Edit Worker"
                        style={{ background: "#1e293b", border: "1px solid var(--border-color)", borderRadius: "6px", padding: "6px 8px", color: "#60a5fa", cursor: "pointer" }}
                        onClick={() => openEdit(w)}
                      >
                        <Edit2 size={15} />
                      </button>
                      <button
                        title="Delete Worker"
                        style={{ background: "#1e293b", border: "1px solid var(--border-color)", borderRadius: "6px", padding: "6px 8px", color: "#f87171", cursor: "pointer" }}
                        onClick={() => handleDelete(wId)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* ADD WORKER MODAL */}
      {showAddModal && (
        <div className="modal-backdrop-ci">
          <div className="modal-content-ci">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3 style={{ margin: 0, color: "#fff", fontSize: "1.2rem" }}>
                Add New Worker to Site
              </h3>
              <button
                style={{ background: "transparent", border: "none", color: "#94a3b8", cursor: "pointer" }}
                onClick={() => setShowAddModal(false)}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreate}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div>
                  <label className="form-label-ci">Worker ID</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    placeholder="e.g. W101"
                    value={formData.worker_id}
                    onChange={(e) => setFormData({ ...formData, worker_id: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Worker Name</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    placeholder="e.g. Rajesh Kumar"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Assigned Task</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    placeholder="e.g. Brick work"
                    value={formData.assigned_task}
                    onChange={(e) => setFormData({ ...formData, assigned_task: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Mobile No</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    placeholder="+91 98765 43210"
                    value={formData.mobile}
                    onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                  />
                </div>
                <div>
                  <label className="form-label-ci">Helmet Status</label>
                  <select
                    className="form-control-ci"
                    value={formData.helmet}
                    onChange={(e) => setFormData({ ...formData, helmet: e.target.value })}
                  >
                    <option value="Yes">Yes (Wearing)</option>
                    <option value="No">No (Missing)</option>
                  </select>
                </div>
                <div>
                  <label className="form-label-ci">Safety Vest Status</label>
                  <select
                    className="form-control-ci"
                    value={formData.vest}
                    onChange={(e) => setFormData({ ...formData, vest: e.target.value })}
                  >
                    <option value="Yes">Yes (Wearing)</option>
                    <option value="No">No (Missing)</option>
                  </select>
                </div>
                <div style={{ gridColumn: "span 2" }}>
                  <label className="form-label-ci">Certification / Trade</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    placeholder="e.g. OSHA-30 Certified, Master Mason"
                    value={formData.certification}
                    onChange={(e) => setFormData({ ...formData, certification: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ marginTop: "24px", display: "flex", justifyContent: "flex-end", gap: "12px" }}>
                <button
                  type="button"
                  className="btn-secondary-ci"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary-ci"
                >
                  Register Worker
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT WORKER MODAL */}
      {showEditModal && selectedWorker && (
        <div className="modal-backdrop-ci">
          <div className="modal-content-ci">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3 style={{ margin: 0, color: "#fff", fontSize: "1.2rem" }}>
                Edit Worker: {selectedWorker.name} ({selectedWorker.worker_id})
              </h3>
              <button
                style={{ background: "transparent", border: "none", color: "#94a3b8", cursor: "pointer" }}
                onClick={() => setShowEditModal(false)}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleUpdate}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div>
                  <label className="form-label-ci">Worker Name</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Assigned Task</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    value={formData.assigned_task}
                    onChange={(e) => setFormData({ ...formData, assigned_task: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Helmet Status</label>
                  <select
                    className="form-control-ci"
                    value={formData.helmet}
                    onChange={(e) => setFormData({ ...formData, helmet: e.target.value })}
                  >
                    <option value="Yes">Yes (Wearing)</option>
                    <option value="No">No (Missing)</option>
                  </select>
                </div>
                <div>
                  <label className="form-label-ci">Safety Vest Status</label>
                  <select
                    className="form-control-ci"
                    value={formData.vest}
                    onChange={(e) => setFormData({ ...formData, vest: e.target.value })}
                  >
                    <option value="Yes">Yes (Wearing)</option>
                    <option value="No">No (Missing)</option>
                  </select>
                </div>
                <div style={{ gridColumn: "span 2" }}>
                  <label className="form-label-ci">Mobile No</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    value={formData.mobile}
                    onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                  />
                </div>
                <div style={{ gridColumn: "span 2" }}>
                  <label className="form-label-ci">Certification</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    value={formData.certification}
                    onChange={(e) => setFormData({ ...formData, certification: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ marginTop: "24px", display: "flex", justifyContent: "flex-end", gap: "12px" }}>
                <button
                  type="button"
                  className="btn-secondary-ci"
                  onClick={() => setShowEditModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary-ci"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
