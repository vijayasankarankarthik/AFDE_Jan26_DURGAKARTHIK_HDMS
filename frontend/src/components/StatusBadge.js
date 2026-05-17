/**
 * components/StatusBadge.js — Coloured pill badge for ticket status.
 */

import React from 'react';
import '../styles/components.css';

const CLASS_MAP = {
  'Open':        'status-open',
  'In Progress': 'status-in-progress',
  'Resolved':    'status-resolved',
  'Closed':      'status-closed',
};

function StatusBadge({ status }) {
  const cls = CLASS_MAP[status] || 'status-closed';
  return (
    <span className={`status-badge ${cls}`}>
      {status}
    </span>
  );
}

export default StatusBadge;
