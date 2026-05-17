/**
 * components/FilterPanel.js — Dropdown filters for status, priority, category.
 *
 * Props:
 *   filters   {Object}    — { status, priority, category } current values
 *   onChange  {function}  — (key, value) => void
 *   onClear   {function}  — resets all filters
 */

import React from 'react';
import '../styles/components.css';

const STATUSES   = ['Open', 'In Progress', 'Resolved', 'Closed'];
const PRIORITIES = ['Low', 'Medium', 'High', 'Critical'];
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

function FilterPanel({ filters, onChange, onClear }) {
  const hasActiveFilters =
    filters.status || filters.priority || filters.category;

  return (
    <div className="filter-panel">
      {/* Status filter */}
      <select
        className="filter-select"
        value={filters.status || ''}
        onChange={(e) => onChange('status', e.target.value)}
        aria-label="Filter by status"
      >
        <option value="">All Statuses</option>
        {STATUSES.map((s) => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      {/* Priority filter */}
      <select
        className="filter-select"
        value={filters.priority || ''}
        onChange={(e) => onChange('priority', e.target.value)}
        aria-label="Filter by priority"
      >
        <option value="">All Priorities</option>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>

      {/* Category filter */}
      <select
        className="filter-select"
        value={filters.category || ''}
        onChange={(e) => onChange('category', e.target.value)}
        aria-label="Filter by category"
      >
        <option value="">All Categories</option>
        {CATEGORIES.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>

      {/* Clear button — only visible when a filter is active */}
      {hasActiveFilters && (
        <button
          type="button"
          className="filter-clear-btn"
          onClick={onClear}
        >
          ✕ Clear filters
        </button>
      )}
    </div>
  );
}

export default FilterPanel;
