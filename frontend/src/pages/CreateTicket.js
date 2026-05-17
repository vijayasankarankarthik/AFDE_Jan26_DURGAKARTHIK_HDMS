/**
 * pages/CreateTicket.js — Full-featured ticket creation form.
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ticketService from '../services/ticketService';
import '../styles/CreateTicket.css';

const CATEGORIES = [
  'VPN Issue',
  'Password Reset',
  'Software Installation',
  'Laptop Issue',
  'Email Access',
  'Network Connectivity',
  'Hardware Request',
  'Other',
];

const PRIORITIES = ['Low', 'Medium', 'High', 'Critical'];

const PRIORITY_ICONS = {
  Low:      '▼',
  Medium:   '●',
  High:     '▲',
  Critical: '⚡',
};

const INITIAL_STATE = {
  employee_name:  '',
  department:     '',
  issue_category: '',
  description:    '',
  priority:       'Medium',
};

function CreateTicket() {
  const navigate = useNavigate();

  const [form, setForm] = useState(INITIAL_STATE);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [createdTicket, setCreatedTicket] = useState(null);

  const validate = () => {
    const errs = {};
    if (!form.employee_name.trim()) errs.employee_name = 'Employee name is required.';
    else if (form.employee_name.trim().length < 2) errs.employee_name = 'Name must be at least 2 characters.';

    if (!form.department.trim()) errs.department = 'Department is required.';

    if (!form.issue_category) errs.issue_category = 'Please select an issue category.';

    if (!form.description.trim()) errs.description = 'Description is required.';
    else if (form.description.trim().length < 10) errs.description = 'Description must be at least 10 characters.';

    return errs;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    // Clear the error for this field on change
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handlePrioritySelect = (priority) => {
    setForm((prev) => ({ ...prev, priority }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setSubmitting(true);
    try {
      const ticket = await ticketService.create({
        employee_name:  form.employee_name.trim(),
        department:     form.department.trim(),
        issue_category: form.issue_category,
        description:    form.description.trim(),
        priority:       form.priority,
      });
      setCreatedTicket(ticket);
    } catch (err) {
      setErrors({ submit: err.message || 'Failed to create ticket. Please try again.' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setForm(INITIAL_STATE);
    setErrors({});
    setCreatedTicket(null);
  };

  /* ── Success screen ─────────────────────────────────────── */
  if (createdTicket) {
    return (
      <div>
        <Navbar breadcrumb="Home / Tickets / New" title="Create Ticket" />
        <div className="page-container create-ticket-page">
          <div className="success-card">
            <div className="success-icon">✅</div>
            <h2 className="success-title">Ticket Created Successfully!</h2>
            <p className="success-message">
              Your support ticket has been submitted and is now in the queue.
            </p>
            <p className="success-ticket-id">Ticket ID: #{createdTicket.ticket_id}</p>
            <div className="success-actions">
              <button className="btn btn-secondary" onClick={handleReset}>
                + Create Another
              </button>
              <button
                className="btn btn-primary"
                onClick={() => navigate(`/tickets/${createdTicket.ticket_id}`)}
              >
                View Ticket
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /* ── Form ───────────────────────────────────────────────── */
  return (
    <div>
      <Navbar breadcrumb="Home / Tickets / New" title="Create Ticket" />

      <div className="page-container create-ticket-page">
        <div className="page-header">
          <h1 className="page-title">Submit a Support Ticket</h1>
          <p className="page-subtitle">
            Fill in the details below and our support team will respond promptly.
          </p>
        </div>

        <div className="create-ticket-layout">
          {/* ── Main form ── */}
          <form onSubmit={handleSubmit} noValidate>
            <div className="form-card">
              <div className="form-card-header">
                <div className="form-card-title">Ticket Information</div>
                <div className="form-card-subtitle">All fields marked with * are required</div>
              </div>

              <div className="form-card-body">
                {errors.submit && (
                  <div
                    className="error-state"
                    style={{ padding: '16px', marginBottom: '20px', background: '#fef2f2', borderRadius: 'var(--radius-sm)', border: '1px solid #fecaca' }}
                  >
                    <span style={{ color: '#dc2626', fontSize: '0.9375rem' }}>⚠️ {errors.submit}</span>
                  </div>
                )}

                <div className="form-grid-2" style={{ gap: '20px' }}>

                  {/* Employee Name */}
                  <div className="form-group">
                    <label className="form-label" htmlFor="employee_name">
                      Employee Name <span className="required">*</span>
                    </label>
                    <input
                      id="employee_name"
                      name="employee_name"
                      type="text"
                      className="form-control"
                      value={form.employee_name}
                      onChange={handleChange}
                      placeholder="e.g. Jane Doe"
                      autoComplete="name"
                    />
                    {errors.employee_name && (
                      <span className="form-error">⚠ {errors.employee_name}</span>
                    )}
                  </div>

                  {/* Department */}
                  <div className="form-group">
                    <label className="form-label" htmlFor="department">
                      Department <span className="required">*</span>
                    </label>
                    <input
                      id="department"
                      name="department"
                      type="text"
                      className="form-control"
                      value={form.department}
                      onChange={handleChange}
                      placeholder="e.g. Engineering"
                    />
                    {errors.department && (
                      <span className="form-error">⚠ {errors.department}</span>
                    )}
                  </div>

                  {/* Issue Category */}
                  <div className="form-group">
                    <label className="form-label" htmlFor="issue_category">
                      Issue Category <span className="required">*</span>
                    </label>
                    <select
                      id="issue_category"
                      name="issue_category"
                      className="form-control"
                      value={form.issue_category}
                      onChange={handleChange}
                      style={{ appearance: 'none', backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E\")", backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', paddingRight: '36px' }}
                    >
                      <option value="">Select a category…</option>
                      {CATEGORIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                    {errors.issue_category && (
                      <span className="form-error">⚠ {errors.issue_category}</span>
                    )}
                  </div>

                </div>

                {/* Description */}
                <div className="form-group" style={{ marginTop: '20px' }}>
                  <label className="form-label" htmlFor="description">
                    Issue Description <span className="required">*</span>
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    className="form-control"
                    value={form.description}
                    onChange={handleChange}
                    placeholder="Please describe the issue in detail. Include any error messages, steps to reproduce, and what you have already tried…"
                    rows={6}
                  />
                  <div className="flex justify-between mt-1">
                    {errors.description ? (
                      <span className="form-error">⚠ {errors.description}</span>
                    ) : (
                      <span />
                    )}
                    <span className="text-xs text-muted">
                      {form.description.length} / 5000
                    </span>
                  </div>
                </div>

                {/* Priority selection */}
                <div className="form-group" style={{ marginTop: '20px' }}>
                  <label className="form-label">Priority Level</label>
                  <div className="priority-group">
                    {PRIORITIES.map((p) => (
                      <div key={p} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <div
                          className={`priority-label priority-label-${p.toLowerCase()}${form.priority === p ? ' selected' : ''}`}
                          onClick={() => handlePrioritySelect(p)}
                          role="button"
                          tabIndex={0}
                          onKeyDown={(e) => e.key === 'Enter' && handlePrioritySelect(p)}
                          style={{ width: '100%', cursor: 'pointer' }}
                        >
                          <span className="priority-label-icon">{PRIORITY_ICONS[p]}</span>
                          <span className="priority-label-text">{p}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Form footer */}
              <div className="form-footer">
                <Link to="/tickets" className="btn btn-secondary">
                  Cancel
                </Link>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? 'Submitting…' : '🎫 Submit Ticket'}
                </button>
              </div>
            </div>
          </form>

          {/* ── Helper panel ── */}
          <div className="create-ticket-helper">
            <div className="helper-title">💡 Tips for faster resolution</div>
            <ul className="helper-list">
              {[
                'Include exact error messages or screenshots if possible.',
                'Describe the steps that led to the issue.',
                'Mention when the problem started.',
                'Note if others in your team are affected.',
                'For urgent issues, set priority to High or Critical.',
                'Password resets are processed within 30 minutes.',
                'Software installs may require manager approval.',
              ].map((tip, i) => (
                <li key={i} className="helper-item">
                  <span className="helper-item-icon">{i + 1}</span>
                  {tip}
                </li>
              ))}
            </ul>

            <div style={{ marginTop: '24px', padding: '16px', background: 'var(--primary-subtle)', borderRadius: 'var(--radius-md)', border: '1px solid var(--primary-light)' }}>
              <div style={{ fontSize: '0.8125rem', fontWeight: '600', color: 'var(--primary)', marginBottom: '6px' }}>
                📞 Emergency Support
              </div>
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                For critical outages, call the IT hotline:<br />
                <strong style={{ color: 'var(--text)' }}>ext. 1234</strong> (internal) <br />
                Available 24/7 for P1 incidents.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CreateTicket;
