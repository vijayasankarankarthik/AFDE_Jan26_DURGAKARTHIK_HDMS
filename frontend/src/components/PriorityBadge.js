/**
 * components/PriorityBadge.js — Coloured label badge for ticket priority.
 */

import React from 'react';
import '../styles/components.css';

const CLASS_MAP = {
  'Low':      'priority-low',
  'Medium':   'priority-medium',
  'High':     'priority-high',
  'Critical': 'priority-critical',
};

const ICONS = {
  'Low':      '▼',
  'Medium':   '●',
  'High':     '▲',
  'Critical': '⚡',
};

function PriorityBadge({ priority }) {
  const cls = CLASS_MAP[priority] || 'priority-medium';
  return (
    <span className={`priority-badge ${cls}`}>
      <span>{ICONS[priority] || '●'}</span>
      {priority}
    </span>
  );
}

export default PriorityBadge;
