/**
 * components/TicketTable.js — Responsive table for listing tickets.
 *
 * Props:
 *   tickets    {Ticket[]}  — array of ticket objects
 *   onDelete   {function}  — (id) => void, called after delete confirmed
 *   loading    {boolean}   — show spinner while loading
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from './StatusBadge';
import PriorityBadge from './PriorityBadge';
import LoadingSpinner from './LoadingSpinner';
import '../styles/components.css';

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function TicketTable({ tickets, onDelete, loading }) {
  const navigate = useNavigate();
  const [confirmDelete, setConfirmDelete] = useState(null);

  const handleDeleteClick = (e, id) => {
    e.stopPropagation();
    setConfirmDelete(id);
  };

  const handleConfirmDelete = async (e) => {
    e.stopPropagation();
    if (onDelete) await onDelete(confirmDelete);
    setConfirmDelete(null);
  };

  if (loading) {
    return <LoadingSpinner text="Loading tickets…" />;
  }

  if (!tickets || tickets.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🎫</div>
        <div className="empty-state-title">No tickets found</div>
        <div className="empty-state-message">
          Try adjusting your search or filters, or create a new ticket to get started.
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="ticket-table-wrapper">
        <table className="ticket-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Employee</th>
              <th>Department</th>
              <th>Category</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((ticket) => (
              <tr
                key={ticket.ticket_id}
                onClick={() => navigate(`/tickets/${ticket.ticket_id}`)}
                style={{ cursor: 'pointer' }}
              >
                <td>
                  <span className="ticket-id-cell">#{ticket.ticket_id}</span>
                </td>
                <td>
                  <span className="ticket-employee-cell">{ticket.employee_name}</span>
                </td>
                <td className="text-sm text-muted">{ticket.department}</td>
                <td className="text-sm">{ticket.issue_category}</td>
                <td>
                  <PriorityBadge priority={ticket.priority} />
                </td>
                <td>
                  <StatusBadge status={ticket.status} />
                </td>
                <td className="text-sm text-muted">
                  {formatDate(ticket.created_at)}
                </td>
                <td>
                  <div className="ticket-actions" onClick={(e) => e.stopPropagation()}>
                    <button
                      className="action-btn action-btn-view"
                      onClick={() => navigate(`/tickets/${ticket.ticket_id}`)}
                    >
                      View
                    </button>
                    {confirmDelete === ticket.ticket_id ? (
                      <>
                        <button
                          className="action-btn action-btn-delete"
                          onClick={handleConfirmDelete}
                        >
                          Confirm
                        </button>
                        <button
                          className="action-btn"
                          style={{ color: 'var(--text-muted)', background: 'var(--surface)', border: '1px solid var(--border)' }}
                          onClick={(e) => { e.stopPropagation(); setConfirmDelete(null); }}
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <button
                        className="action-btn action-btn-delete"
                        onClick={(e) => handleDeleteClick(e, ticket.ticket_id)}
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default TicketTable;
