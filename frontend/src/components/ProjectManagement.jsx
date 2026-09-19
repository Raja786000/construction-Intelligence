import React, { useState, useEffect } from "react";
import {
  Plus,
  Edit2,
  Trash2,
  Eye,
  Building2,
  Calendar,
  MapPin,
  IndianRupee,
  Search,
  CheckCircle,
  Clock,
  X
} from "lucide-react";

export default function ProjectManagement({ activeProject, setActiveProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  // Modal States
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [viewDetails, setViewDetails] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    name: "Metro Bridge",
    client: "ABC Construction",
    budget: 20.0,
    spent: 1.8,
    location: "Hyderabad",
    start_date: "2024-01-10",
    end_date: "2025-08-30",
    project_type: "Infrastructure",
    actual_progress: 68.0,
    planned_progress: 70.0
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://127.0.0.1:8000/api/projects");
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
      }
    } catch (err) {
      console.error("Error loading projects:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:8000/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setShowAddModal(false);
        fetchProjects();
      }
    } catch (err) {
      console.error("Failed to create project:", err);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!selectedProject) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/projects/${selectedProject._id || selectedProject.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setShowEditModal(false);
        fetchProjects();
      }
    } catch (err) {
      console.error("Failed to update project:", err);
    }
  };

  const handleDelete = async (projectId) => {
    if (!window.confirm("Are you sure you want to delete this project from MongoDB?")) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        fetchProjects();
      }
    } catch (err) {
      console.error("Failed to delete project:", err);
    }
  };

  const handleView = async (project) => {
    setSelectedProject(project);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/projects/${project._id || project.id}`);
      if (res.ok) {
        const data = await res.json();
        setViewDetails(data);
        setShowViewModal(true);
      }
    } catch (err) {
      console.error("Failed to view project details:", err);
    }
  };

  const openEdit = (project) => {
    setSelectedProject(project);
    setFormData({
      name: project.name || "",
      client: project.client || "",
      budget: project.budget || 10.0,
      spent: project.spent || 0.0,
      location: project.location || "",
      start_date: project.start_date || "",
      end_date: project.planned_end_date || project.end_date || "",
      project_type: project.type || "Infrastructure",
      actual_progress: project.actual_progress || 0.0,
      planned_progress: project.planned_progress || 0.0
    });
    setShowEditModal(true);
  };

  const filteredProjects = projects.filter((p) => {
    const s = searchTerm.toLowerCase();
    return (
      (p.name && p.name.toLowerCase().includes(s)) ||
      (p.client && p.client.toLowerCase().includes(s)) ||
      (p.location && p.location.toLowerCase().includes(s)) ||
      (p.id && p.id.toLowerCase().includes(s))
    );
  });

  return (
    <div>
      {/* Header Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: "700", color: "#fff", margin: "0 0 4px 0" }}>
            Project Management (MongoDB)
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Create, update, view and track construction projects with live milestones and budgets
          </p>
        </div>

        <button
          className="btn-primary-ci"
          onClick={() => {
            setFormData({
              name: "Metro Bridge",
              client: "ABC Construction",
              budget: 20.0,
              spent: 1.8,
              location: "Hyderabad",
              start_date: "2024-01-10",
              end_date: "2025-08-30",
              project_type: "Infrastructure",
              actual_progress: 68.0,
              planned_progress: 70.0
            });
            setShowAddModal(true);
          }}
        >
          <Plus size={18} /> Add Project
        </button>
      </div>

      {/* Search Bar */}
      <div style={{ marginBottom: "20px", position: "relative", maxWidth: "400px" }}>
        <Search size={18} style={{ position: "absolute", left: "14px", top: "12px", color: "var(--text-muted)" }} />
        <input
          type="text"
          className="form-control-ci"
          style={{ paddingLeft: "42px" }}
          placeholder="Search by project name, client, or location..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Projects Table */}
      <div className="ci-table-wrap">
        <table className="ci-table">
          <thead>
            <tr>
              <th>Project Name & ID</th>
              <th>Client</th>
              <th>Budget (₹ Cr)</th>
              <th>Location</th>
              <th>Progress</th>
              <th>Schedule Status</th>
              <th>Timeline</th>
              <th style={{ textAlign: "right" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredProjects.map((p) => {
              const pId = p._id || p.id;
              const isSelected = activeProject === pId;
              const budgetVal = p.budget || 20.0;
              const spentVal = p.spent || 0.0;

              return (
                <tr
                  key={pId}
                  style={{ backgroundColor: isSelected ? "rgba(59, 130, 246, 0.08)" : "transparent" }}
                >
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <div style={{
                        width: "34px",
                        height: "34px",
                        borderRadius: "8px",
                        background: "rgba(59, 130, 246, 0.15)",
                        color: "#60a5fa",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center"
                      }}>
                        <Building2 size={18} />
                      </div>
                      <div>
                        <strong style={{ color: "#fff", display: "block" }}>{p.name}</strong>
                        <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>ID: {pId}</span>
                      </div>
                    </div>
                  </td>
                  <td>{p.client || "ABC Construction"}</td>
                  <td>
                    <span style={{ color: "#38bdf8", fontWeight: "600" }}>₹ {budgetVal} Cr</span>
                    <span style={{ display: "block", fontSize: "0.72rem", color: "var(--text-muted)" }}>
                      Spent: ₹ {spentVal} Cr
                    </span>
                  </td>
                  <td>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                      <MapPin size={13} color="#94a3b8" /> {p.location || "Hyderabad"}
                    </span>
                  </td>
                  <td style={{ minWidth: "130px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", marginBottom: "4px" }}>
                      <span>{p.actual_progress || 0}%</span>
                      <span style={{ color: "var(--text-muted)" }}>Plan: {p.planned_progress || 0}%</span>
                    </div>
                    <div style={{ width: "100%", height: "6px", backgroundColor: "#334155", borderRadius: "9999px", overflow: "hidden" }}>
                      <div style={{
                        width: `${Math.min(100, p.actual_progress || 0)}%`,
                        height: "100%",
                        backgroundColor: (p.actual_progress || 0) >= (p.planned_progress || 0) ? "#10b981" : "#f59e0b"
                      }} />
                    </div>
                  </td>
                  <td>
                    <span className={`badge-pill ${
                      (p.schedule_status || "").includes("Ahead") || (p.schedule_status || "").includes("On Track") || (p.schedule_status || "").includes("On Schedule")
                        ? "badge-success"
                        : "badge-danger"
                    }`}>
                      {p.schedule_status || "On Schedule"}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                      {p.start_date} → {p.planned_end_date || p.end_date}
                    </span>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <div style={{ display: "inline-flex", gap: "6px" }}>
                      <button
                        title="View Details"
                        style={{ background: "#1e293b", border: "1px solid var(--border-color)", borderRadius: "6px", padding: "6px 8px", color: "#94a3b8", cursor: "pointer" }}
                        onClick={() => handleView(p)}
                      >
                        <Eye size={15} />
                      </button>
                      <button
                        title="Edit Project"
                        style={{ background: "#1e293b", border: "1px solid var(--border-color)", borderRadius: "6px", padding: "6px 8px", color: "#60a5fa", cursor: "pointer" }}
                        onClick={() => openEdit(p)}
                      >
                        <Edit2 size={15} />
                      </button>
                      <button
                        title="Delete Project"
                        style={{ background: "#1e293b", border: "1px solid var(--border-color)", borderRadius: "6px", padding: "6px 8px", color: "#f87171", cursor: "pointer" }}
                        onClick={() => handleDelete(pId)}
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

      {/* ADD PROJECT MODAL */}
      {showAddModal && (
        <div className="modal-backdrop-ci">
          <div className="modal-content-ci">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3 style={{ margin: 0, color: "#fff", fontSize: "1.2rem" }}>
                Add New Project (MongoDB)
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
                  <label className="form-label-ci">Project Name</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    placeholder="e.g. Metro Bridge"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Client</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    placeholder="e.g. ABC Construction"
                    value={formData.client}
                    onChange={(e) => setFormData({ ...formData, client: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Budget (₹ in Crores)</label>
                  <input
                    type="number"
                    step="0.1"
                    className="form-control-ci"
                    placeholder="e.g. 20"
                    value={formData.budget}
                    onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Spent to Date (₹ Cr)</label>
                  <input
                    type="number"
                    step="0.1"
                    className="form-control-ci"
                    placeholder="e.g. 1.8"
                    value={formData.spent}
                    onChange={(e) => setFormData({ ...formData, spent: parseFloat(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="form-label-ci">Location</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    placeholder="e.g. Hyderabad"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Project Type</label>
                  <select
                    className="form-control-ci"
                    value={formData.project_type}
                    onChange={(e) => setFormData({ ...formData, project_type: e.target.value })}
                  >
                    <option value="Infrastructure">Infrastructure</option>
                    <option value="Commercial">Commercial</option>
                    <option value="Residential">Residential</option>
                    <option value="Institutional">Institutional</option>
                  </select>
                </div>
                <div>
                  <label className="form-label-ci">Start Date</label>
                  <input
                    type="date"
                    className="form-control-ci"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">End Date</label>
                  <input
                    type="date"
                    className="form-control-ci"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Actual Progress (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    className="form-control-ci"
                    value={formData.actual_progress}
                    onChange={(e) => setFormData({ ...formData, actual_progress: parseFloat(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="form-label-ci">Planned Progress (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    className="form-control-ci"
                    value={formData.planned_progress}
                    onChange={(e) => setFormData({ ...formData, planned_progress: parseFloat(e.target.value) })}
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
                  Save to MongoDB
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT PROJECT MODAL */}
      {showEditModal && selectedProject && (
        <div className="modal-backdrop-ci">
          <div className="modal-content-ci">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3 style={{ margin: 0, color: "#fff", fontSize: "1.2rem" }}>
                Edit Project: {selectedProject.name}
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
                  <label className="form-label-ci">Project Name</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Client</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    value={formData.client}
                    onChange={(e) => setFormData({ ...formData, client: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Budget (₹ in Cr)</label>
                  <input
                    type="number"
                    step="0.1"
                    className="form-control-ci"
                    value={formData.budget}
                    onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Spent to Date (₹ Cr)</label>
                  <input
                    type="number"
                    step="0.1"
                    className="form-control-ci"
                    value={formData.spent}
                    onChange={(e) => setFormData({ ...formData, spent: parseFloat(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="form-label-ci">Location</label>
                  <input
                    type="text"
                    className="form-control-ci"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label-ci">Actual Progress (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    className="form-control-ci"
                    value={formData.actual_progress}
                    onChange={(e) => setFormData({ ...formData, actual_progress: parseFloat(e.target.value) })}
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
                  Update Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* VIEW PROJECT DETAILS MODAL */}
      {showViewModal && viewDetails && (
        <div className="modal-backdrop-ci">
          <div className="modal-content-ci" style={{ maxWidth: "700px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
              <div>
                <h3 style={{ margin: 0, color: "#fff", fontSize: "1.25rem" }}>
                  {viewDetails.project.name}
                </h3>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  Client: {viewDetails.project.client} | Location: {viewDetails.project.location}
                </span>
              </div>
              <button
                style={{ background: "transparent", border: "none", color: "#94a3b8", cursor: "pointer" }}
                onClick={() => setShowViewModal(false)}
              >
                <X size={20} />
              </button>
            </div>

            {/* Quick Metrics */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "10px", marginBottom: "20px" }}>
              <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "10px", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>BUDGET</span>
                <div style={{ fontWeight: "700", color: "#38bdf8", fontSize: "1rem" }}>
                  ₹ {viewDetails.project.budget || 20.0} Cr
                </div>
              </div>
              <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "10px", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>SPENT</span>
                <div style={{ fontWeight: "700", color: "#fff", fontSize: "1rem" }}>
                  ₹ {viewDetails.project.spent || 1.8} Cr
                </div>
              </div>
              <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "10px", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>PROGRESS</span>
                <div style={{ fontWeight: "700", color: "#34d399", fontSize: "1rem" }}>
                  {viewDetails.project.actual_progress || 68}%
                </div>
              </div>
              <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "10px", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>STATUS</span>
                <div style={{ fontWeight: "700", color: "#fbbf24", fontSize: "0.9rem" }}>
                  {viewDetails.project.schedule_status || "On Track"}
                </div>
              </div>
            </div>

            {/* Tasks & Milestones */}
            <h4 style={{ color: "#fff", fontSize: "1rem", marginBottom: "10px" }}>
              Active Tasks ({viewDetails.tasks.length})
            </h4>
            <div style={{ maxHeight: "180px", overflowY: "auto", marginBottom: "20px", border: "1px solid var(--border-color)", borderRadius: "8px" }}>
              {viewDetails.tasks.map((t, idx) => (
                <div key={idx} style={{ padding: "8px 12px", borderBottom: "1px solid rgba(255, 255, 255, 0.05)", display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                  <span style={{ color: "#f8fafc" }}>{t.name}</span>
                  <span style={{ color: t.status === "Completed" ? "#34d399" : "#60a5fa" }}>
                    {t.status} ({t.progress}%)
                  </span>
                </div>
              ))}
            </div>

            <h4 style={{ color: "#fff", fontSize: "1rem", marginBottom: "10px" }}>
              Milestones ({viewDetails.milestones.length})
            </h4>
            <div style={{ maxHeight: "150px", overflowY: "auto", border: "1px solid var(--border-color)", borderRadius: "8px" }}>
              {viewDetails.milestones.map((m, idx) => (
                <div key={idx} style={{ padding: "8px 12px", borderBottom: "1px solid rgba(255, 255, 255, 0.05)", display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                  <span style={{ color: "#f8fafc" }}>{m.name}</span>
                  <span style={{ color: m.status === "Completed" ? "#34d399" : "#fbbf24" }}>
                    Due: {m.due_date} ({m.status})
                  </span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: "20px", display: "flex", justifyContent: "flex-end" }}>
              <button
                className="btn-primary-ci"
                onClick={() => setShowViewModal(false)}
              >
                Close View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
