/**
 * pages/Dashboard.js — Main dashboard showing stats and recent tickets.
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ticketService from '../services/ticketService';
import '../styles/Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentTickets, setRecentTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      setError(null);
      try {
        const [statsData, ticketsData] = await Promise.all([
          ticketService.getStats(),
          ticketService.getAll(1, 8),
        ]);
        setStats(statsData);
        setRecentTickets(ticketsData.tickets);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, []);

  const formatDate = (dateStr) =>
    new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });

  const getProgressWidth = (count) => {
    if (!stats || stats.total_tickets === 0) return '0%';
    return `${Math.round((count / stats.total_tickets) * 100)}%`;
  };

  const getProgressColor = (status) => {
    const map = {
      Open:        'var(--status-open)',
      'In Progress':'var(--status-progress)',
      Resolved:    'var(--status-resolved)',
      Closed:      'var(--status-closed)',
    };
    return map[status] || 'var(--primary)';
  };

  if (loading) {
    return (
      <div>
        <Navbar breadcrumb="Home" title="Dashboard" />
        <div className="page-container"><LoadingSpinner text="Loading dashboard…" /></div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Navbar breadcrumb="Home" title="Dashboard" />
        <div className="page-container">
          <div className="error-state">
            <div className="error-state-icon">⚠️</div>
            <div className="error-state-title">Failed to load dashboard</div>
            <div className="error-state-message">{error}</div>
            <button className="btn btn-primary mt-4" onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const statusRows = [
    { label: 'Open',        count: stats.open_tickets,        status: 'Open' },
    { label: 'In Progress', count: stats.in_progress_tickets, status: 'In Progress' },
    { label: 'Resolved',    count: stats.resolved_tickets,    status: 'Resolved' },
    { label: 'Closed',      count: stats.closed_tickets,      status: 'Closed' },
  ];

  return (
    <div>
      <Navbar breadcrumb="Home" title="Dashboard">
        <span className="topbar-badge">
          📅 {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
        </span>
      </Navbar>

      <div className="page-container dashboard-page">
        {/* Page Header */}
        <div className="page-header">
          <h1 className="page-title">Welcome back 👋</h1>
          <p className="page-subtitle">Here's an overview of your helpdesk system today.</p>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <StatCard
            label="Total Tickets"
            value={stats.total_tickets}
            sub="All time"
            icon="🎫"
            iconClass="icon-blue"
          />
          <StatCard
            label="Open"
            value={stats.open_tickets}
            sub="Awaiting action"
            icon="📬"
            iconClass="icon-amber"
          />
          <StatCard
            label="In Progress"
            value={stats.in_progress_tickets}
            sub="Being worked on"
            icon="⚙️"
            iconClass="icon-cyan"
          />
          <StatCard
            label="Resolved"
            value={stats.resolved_tickets}
            sub="Successfully closed"
            icon="✅"
            iconClass="icon-green"
          />
          <StatCard
            label="Critical"
            value={stats.critical_tickets}
            sub="Needs immediate attention"
            icon="🚨"
            iconClass="icon-red"
          />
          <StatCard
            label="High Priority"
            value={stats.high_priority_tickets}
            sub="Escalated tickets"
            icon="⚡"
            iconClass="icon-purple"
          />
        </div>

        {/* Dashboard Body */}
        <div className="dashboard-body">
          {/* Left: Recent Tickets */}
          <div>
            <div className="section-header">
              <span className="section-title">Recent Tickets</span>
              <Link to="/tickets" className="section-link">View all →</Link>
            </div>
            <div className="ticket-table-wrapper">
              {recentTickets.length === 0 ? (
                <div className="empty-state" style={{ padding: '40px' }}>
                  <div className="empty-state-icon">📭</div>
                  <div className="empty-state-title">No tickets yet</div>
                  <div className="empty-state-message">
                    Create your first ticket to get started.
                  </div>
                </div>
              ) : (
                <table className="ticket-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Employee</th>
                      <th>Category</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentTickets.map((ticket) => (
                      <tr
                        key={ticket.ticket_id}
                        style={{ cursor: 'pointer' }}
                        onClick={() => navigate(`/tickets/${ticket.ticket_id}`)}
                      >
                        <td>
                          <span className="ticket-id-cell">#{ticket.ticket_id}</span>
                        </td>
                        <td>
                          <div className="ticket-employee-cell">{ticket.employee_name}</div>
                          <div className="text-xs text-muted">{ticket.department}</div>
                        </td>
                        <td className="text-sm">{ticket.issue_category}</td>
                        <td><PriorityBadge priority={ticket.priority} /></td>
                        <td><StatusBadge status={ticket.status} /></td>
                        <td className="text-sm text-muted">{formatDate(ticket.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Right: Status distribution + Quick actions */}
          <div>
            {/* Status distribution */}
            <div className="status-distribution">
              <div className="section-title">Status Distribution</div>
              <div className="distribution-list">
                {statusRows.map(({ label, count, status }) => (
                  <div key={label} className="distribution-item">
                    <div className="distribution-row">
                      <span className="distribution-label">{label}</span>
                      <span className="distribution-count">{count}</span>
                    </div>
                    <div className="progress-bar-outer">
                      <div
                        className="progress-bar-inner"
                        style={{
                          width: getProgressWidth(count),
                          background: getProgressColor(status),
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick actions */}
            <div className="quick-actions">
              <div className="section-title">Quick Actions</div>
              <div className="quick-action-grid">
                <Link to="/tickets/new" className="quick-action-btn">
                  <span className="quick-action-icon">➕</span>
                  <span className="quick-action-label">New Ticket</span>
                </Link>
                <Link to="/tickets" className="quick-action-btn">
                  <span className="quick-action-icon">📋</span>
                  <span className="quick-action-label">All Tickets</span>
                </Link>
                <Link to="/tickets?status=Open" className="quick-action-btn">
                  <span className="quick-action-icon">📬</span>
                  <span className="quick-action-label">Open Tickets</span>
                </Link>
                <Link to="/tickets?priority=Critical" className="quick-action-btn">
                  <span className="quick-action-icon">🚨</span>
                  <span className="quick-action-label">Critical</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
