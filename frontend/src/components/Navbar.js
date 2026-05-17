/**
 * components/Navbar.js — Page-level topbar with breadcrumb and actions.
 * Receives title, breadcrumb, and optional right-slot children as props.
 */

import React from 'react';
import '../styles/components.css';

function Navbar({ breadcrumb, title, children }) {
  return (
    <header className="topbar">
      <div className="topbar-left">
        {breadcrumb && <span className="topbar-breadcrumb">{breadcrumb}</span>}
        {title && <span className="topbar-title">{title}</span>}
      </div>
      {children && <div className="topbar-right">{children}</div>}
    </header>
  );
}

export default Navbar;
