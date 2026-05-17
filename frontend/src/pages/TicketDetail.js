/**
 * pages/TicketDetail.js — Full ticket detail view with inline editing.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ticketService from '../services/ticketService';
import '../styles/TicketDetail.css';

const STATUSES    = ['Open', 'In Progress', 'Resolved', 'Closed'];
const PRIORITIES  = ['Low', 'Medium', 'High', 'Critical'];
const CATEGORIES  = [
  'VPN Issue', 'Password Reset', 'Software Installation',
  'Laptop Issue', 'Email Access', 'Network Connectivity',
  'Hardware Request', 'Other',
];

function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'long', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function Toast({ message, type, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3500);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`toast toast-${type}`}>
      {type === 'success' ? '✅' : '⚠️'} {message}
    </div>
  );
}

function TicketDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit state
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [saving, setSaving] = useState(false);

  // Toast
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  const loadTicket = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ticketService.getById(id);
      setTicket(data);
      setEditForm({
        status:           data.status,
        priority:         data.priority,
        issue_category:   data.issue_category,
        description:      data.description,
        resolution_notes: data.resolution_notes || '',
        employee_name:    data.employee_name,
        department:       data.department,
      });
    } catch (err) {
      setError(err.message || 'Failed to load ticket.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadTicket();
  }, [loadTicket]);

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await ticketService.update(id, {
        status:           editForm.status,
        priority:         editForm.priority,
        issue_category:   editForm.issue_category,
        description:      editForm.description || undefined,
        resolution_notes: editForm.resolution_notes || undefined,
        employee_name:    editForm.employee_name || undefined,
        department:       editForm.department || undefined,
      });
      setTicket(updated);
      setEditing(false);
      showToast('Ticket updated successfully.');
    } catch (err) {
      showToast(err.message || 'Update failed.', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to permanently delete ticket #${id}? This cannot be undone.`)) return;
    try {
      await ticketService.remove(id);
      navigate('/tickets', { replace: true });
    } catch (err) {
      showToast(err.message || 'Delete failed.', 'error');
    }
  };

  /* ── Loading / error states ─────────────────────────────── */
  if (loading) {
    return (
      <div>
        <Navbar breadcrumb="Home / Tickets / Detail" title="Ticket Detail" />
        <div className="page-container"><LoadingSpinner text="Loading ticket…" /></div>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div>
        <Navbar breadcrumb="Home / Tickets / Detail" title="Ticket Detail" />
        <div className="page-container">
          <div className="error-state">
            <div className="error-state-icon">🔍</div>
            <div className="error-state-title">Ticket not found</div>
            <div className="error-state-message">{error || `Ticket #${id} does not exist.`}</div>
            <button className="btn btn-primary mt-4" onClick={() => navigate('/tickets')}>
              ← Back to Tickets
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar
        breadcrumb={`Home / Tickets / #${ticket.ticket_id}`}
        title={`Ticket #${ticket.ticket_id}`}
      >
        <StatusBadge status={ticket.status} />
        <PriorityBadge priority={ticket.priority} />
      </Navbar>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="page-container ticket-detail-page">
        {/* Back link */}
        <button className="back-link" onClick={() => navigate('/tickets')}>
          ← Back to All Tickets
        </button>

        <div className="detail-layout">
          {/* ── Left: Ticket info ── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

            {/* Main info card */}
            <div className="detail-card">
              <div className="detail-card-header">
                <span className="detail-card-title">Ticket Information</span>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {!editing && (
                    <button className="btn btn-secondary btn-sm" onClick={() => setEditing(true)}>
                      ✏️ Edit
                    </button>
                  )}
                </div>
              </div>
              <div className="detail-card-body">
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Ticket ID</span>
                    <span className="info-value-mono">#{ticket.ticket_id}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Employee</span>
                    {editing ? (
                      <input
                        name="employee_name"
                        className="form-control"
                        value={editForm.employee_name}
                        onChange={handleEditChange}
                      />
                    ) : (
                      <span className="info-value">{ticket.employee_name}</span>
                    )}
                  </div>
                  <div className="info-item">
                    <span className="info-label">Department</span>
                    {editing ? (
                      <input
                        name="department"
                        className="form-control"
                        value={editForm.department}
                        onChange={handleEditChange}
                      />
                    ) : (
                      <span className="info-value">{ticket.department}</span>
                    )}
                  </div>
                  <div className="info-item">
                    <span className="info-label">Category</span>
                    {editing ? (
                      <select
                        name="issue_category"
                        className="form-control"
                        value={editForm.issue_category}
                        onChange={handleEditChange}
                      >
                        {CATEGORIES.map((c) => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    ) : (
                      <span className="info-value">{ticket.issue_category}</span>
                    )}
                  </div>
                  <div className="info-item">
                    <span className="info-label">Status</span>
                    {editing ? (
                      <select
                        name="status"
                        className="form-control"
                        value={editForm.status}
                        onChange={handleEditChange}
                      >
                        {STATUSES.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    ) : (
                      <StatusBadge status={ticket.status} />
                    )}
                  </div>
                  <div className="info-item">
                    <span className="info-label">Priority</span>
                    {editing ? (
                      <select
                        name="priority"
                        className="form-control"
                        value={editForm.priority}
                        onChange={handleEditChange}
                      >
                        {PRIORITIES.map((p) => (
                          <option key={p} value={p}>{p}</option>
                        ))}
                      </select>
                    ) : (
                      <PriorityBadge priority={ticket.priority} />
                    )}
                  </div>
                </div>

                {/* Description */}
                <div style={{ marginTop: '8px' }}>
                  <div className="info-label" style={{ marginBottom: '8px' }}>Description</div>
                  {editing ? (
                    <textarea
                      name="description"
                      className="form-control"
                      value={editForm.description}
                      onChange={handleEditChange}
                      rows={6}
                    />
                  ) : (
                    <div className="description-block">{ticket.description}</div>
                  )}
                </div>

                {/* Edit actions */}
                {editing && (
                  <div className="edit-actions" style={{ marginTop: '20px' }}>
                    <button
                      className="btn btn-primary"
                      onClick={handleSave}
                      disabled={saving}
                    >
                      {saving ? 'Saving…' : '💾 Save Changes'}
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setEditing(false);
                        // Reset form back to current ticket values
                        setEditForm({
                          status: ticket.status, priority: ticket.priority,
                          issue_category: ticket.issue_category, description: ticket.description,
                          resolution_notes: ticket.resolution_notes || '',
                          employee_name: ticket.employee_name, department: ticket.department,
                        });
                      }}
                      disabled={saving}
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Resolution Notes card */}
            <div className="detail-card">
              <div className="detail-card-header">
                <span className="detail-card-title">Resolution Notes</span>
              </div>
              <div className="detail-card-body">
                {editing ? (
                  <div className="form-group">
                    <label className="form-label" htmlFor="resolution_notes">
                      Add or update resolution notes
                    </label>
                    <textarea
                      id="resolution_notes"
                      name="resolution_notes"
                      className="form-control"
                      value={editForm.resolution_notes}
                      onChange={handleEditChange}
                      rows={5}
                      placeholder="Describe how the issue was resolved…"
                    />
                  </div>
                ) : ticket.resolution_notes ? (
                  <div className="resolution-block">{ticket.resolution_notes}</div>
                ) : (
                  <p className="resolution-empty">
                    No resolution notes yet. Notes will appear here once the issue is being worked on or resolved.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* ── Right: Meta + Actions ── */}
          <div className="side-panel">
            {/* Metadata */}
            <div className="meta-card">
              <div className="meta-card-title">Ticket Metadata</div>
              <div className="meta-list">
                <div className="meta-row">
                  <span className="meta-key">Ticket ID</span>
                  <span className="meta-value" style={{ fontFamily: 'JetBrains Mono, monospace', color: 'var(--primary)' }}>
                    #{ticket.ticket_id}
                  </span>
                </div>
                <div className="meta-divider" />
                <div className="meta-row">
                  <span className="meta-key">Status</span>
                  <StatusBadge status={ticket.status} />
                </div>
                <div className="meta-row">
                  <span className="meta-key">Priority</span>
                  <PriorityBadge priority={ticket.priority} />
                </div>
                <div className="meta-divider" />
                <div className="meta-row">
                  <span className="meta-key">Created</span>
                  <span className="meta-value" style={{ fontSize: '0.75rem' }}>
                    {formatDateTime(ticket.created_at)}
                  </span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">Last Updated</span>
                  <span className="meta-value" style={{ fontSize: '0.75rem' }}>
                    {formatDateTime(ticket.updated_at)}
                  </span>
                </div>
              </div>
            </div>

            {/* Quick status update */}
            {!editing && (
              <div className="meta-card">
                <div className="meta-card-title">Quick Status Update</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                  {STATUSES.filter((s) => s !== ticket.status).map((s) => (
                    <button
                      key={s}
                      className="btn btn-secondary btn-sm"
                      style={{ justifyContent: 'flex-start', width: '100%' }}
                      onClick={async () => {
                        try {
                          const updated = await ticketService.update(id, { status: s });
                          setTicket(updated);
                          setEditForm((prev) => ({ ...prev, status: s }));
                          showToast(`Status changed to "${s}"`);
                        } catch (err) {
                          showToast(err.message, 'error');
                        }
                      }}
                    >
                      → Mark as {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Danger zone */}
            <div className="danger-zone">
              <div className="danger-zone-title">⚠ Danger Zone</div>
              <p className="danger-zone-text">
                Permanently deleting a ticket cannot be undone. All associated data will be lost.
              </p>
              <button
                className="btn btn-danger btn-sm"
                style={{ width: '100%' }}
                onClick={handleDelete}
              >
                🗑 Delete Ticket
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TicketDetail;
