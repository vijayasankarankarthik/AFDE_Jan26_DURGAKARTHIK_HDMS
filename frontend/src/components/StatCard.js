/**
 * components/StatCard.js — Metric card used on the Dashboard.
 *
 * Props:
 *   label     {string}  — metric label
 *   value     {number}  — metric value
 *   sub       {string}  — optional sub-text
 *   icon      {string}  — emoji or character icon
 *   iconClass {string}  — CSS class for icon background colour
 */

import React from 'react';
import '../styles/components.css';

function StatCard({ label, value, sub, icon, iconClass = 'icon-blue' }) {
  return (
    <div className="stat-card">
      <div className="stat-card-info">
        <span className="stat-card-label">{label}</span>
        <span className="stat-card-value">{value ?? '—'}</span>
        {sub && <span className="stat-card-sub">{sub}</span>}
      </div>
      <div className={`stat-card-icon ${iconClass}`}>
        {icon}
      </div>
    </div>
  );
}

export default StatCard;
