/**
 * components/SearchBar.js — Controlled search input with icon.
 *
 * Props:
 *   value       {string}    — controlled value
 *   onChange    {function}  — change handler
 *   placeholder {string}    — input placeholder text
 */

import React from 'react';
import '../styles/components.css';

function SearchBar({ value, onChange, placeholder = 'Search tickets…' }) {
  return (
    <div className="search-bar">
      <span className="search-bar-icon" aria-hidden="true">🔍</span>
      <input
        type="search"
        className="search-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label="Search tickets"
        autoComplete="off"
        spellCheck={false}
      />
    </div>
  );
}

export default SearchBar;
