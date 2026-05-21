/**
 * components/Sidebar.js — Fixed left navigation sidebar.
 */

import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import '../styles/components.css';

const navItems = [
  { to: '/dashboard', icon: '📊', label: 'Dashboard' },
  { to: '/tickets',   icon: '🎫', label: 'All Tickets' },
  { to: '/tickets/new', icon: '➕', label: 'New Ticket' },
];

const analyticsItems = [
  { to: '/analytics', icon: '📈', label: 'Analytics' },
  { to: '/upload',    icon: '⬆',  label: 'Import CSV' },
  { to: '/reports',   icon: '📋', label: 'Reports' },
];

function Sidebar() {
  const location = useLocation();

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">🖥️</div>
          <div className="sidebar-logo-text">
            <span className="sidebar-logo-title">Helpdesk</span>
            <span className="sidebar-logo-subtitle">Ticket System</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <span className="sidebar-section-label">Main Menu</span>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `nav-link${isActive || (item.to === '/tickets' && location.pathname.startsWith('/tickets') && location.pathname !== '/tickets/new') ? ' active' : ''}`
            }
            end={item.to === '/tickets'}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}

        <span className="sidebar-section-label" style={{ marginTop: '20px' }}>Analytics</span>
        {analyticsItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}

        <span className="sidebar-section-label" style={{ marginTop: '8px' }}>System</span>
        <a
          href="/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="nav-link"
        >
          <span className="nav-icon">📖</span>
          API Docs
        </a>
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-version">v2.0.0 · Phase 2</div>
      </div>
    </aside>
  );
}

export default Sidebar;
