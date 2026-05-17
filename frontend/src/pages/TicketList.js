/**
 * pages/TicketList.js — Searchable, filterable, paginated ticket listing.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import SearchBar from '../components/SearchBar';
import FilterPanel from '../components/FilterPanel';
import TicketTable from '../components/TicketTable';
import ticketService from '../services/ticketService';
import useDebounce from '../hooks/useDebounce';
import '../styles/TicketList.css';

const PAGE_SIZE = 15;

function TicketList() {
  const [searchParams] = useSearchParams();

  const [tickets, setTickets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    status:   searchParams.get('status')   || '',
    priority: searchParams.get('priority') || '',
    category: '',
  });

  const debouncedQuery = useDebounce(searchQuery, 400);

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const isFiltered = debouncedQuery || filters.status || filters.priority || filters.category;
      let data;
      if (isFiltered) {
        data = await ticketService.search({
          q: debouncedQuery || undefined,
          status:   filters.status   || undefined,
          priority: filters.priority || undefined,
          category: filters.category || undefined,
          page,
          page_size: PAGE_SIZE,
        });
      } else {
        data = await ticketService.getAll(page, PAGE_SIZE);
      }
      setTickets(data.tickets);
      setTotal(data.total);
    } catch (err) {
      setError(err.message || 'Failed to load tickets.');
    } finally {
      setLoading(false);
    }
  }, [debouncedQuery, filters, page]);

  // Reset to page 1 when query/filters change
  useEffect(() => {
    setPage(1);
  }, [debouncedQuery, filters]);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setFilters({ status: '', priority: '', category: '' });
  };

  const handleDelete = async (id) => {
    try {
      await ticketService.remove(id);
      fetchTickets();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <Navbar breadcrumb="Home / Tickets" title="All Tickets">
        <Link to="/tickets/new" className="btn btn-primary btn-sm">
          + New Ticket
        </Link>
      </Navbar>

      <div className="page-container ticket-list-page">
        <div className="page-header">
          <h1 className="page-title">Ticket Management</h1>
          <p className="page-subtitle">
            Browse, search, and manage all helpdesk support tickets.
          </p>
        </div>

        {/* Toolbar */}
        <div className="ticket-list-toolbar">
          <div className="toolbar-top">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search by employee, description, category…"
            />
          </div>
          <div className="toolbar-filters">
            <FilterPanel
              filters={filters}
              onChange={handleFilterChange}
              onClear={handleClearFilters}
            />
          </div>
          <div className="tickets-count-bar">
            <span className="tickets-count-text">
              Showing <strong>{tickets.length}</strong> of <strong>{total}</strong> ticket{total !== 1 ? 's' : ''}
            </span>
          </div>
        </div>

        {/* Error state */}
        {error && (
          <div className="error-state" style={{ marginBottom: '20px' }}>
            <div className="error-state-icon">⚠️</div>
            <div className="error-state-title">Error loading tickets</div>
            <div className="error-state-message">{error}</div>
            <button className="btn btn-primary mt-4" onClick={fetchTickets}>Retry</button>
          </div>
        )}

        {/* Table */}
        {!error && (
          <TicketTable
            tickets={tickets}
            onDelete={handleDelete}
            loading={loading}
          />
        )}

        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="pagination">
            <span className="pagination-info">
              Page {page} of {totalPages}
            </span>
            <div className="pagination-controls">
              <button
                className="pagination-btn"
                onClick={() => setPage(1)}
                disabled={page === 1}
              >
                «
              </button>
              <button
                className="pagination-btn"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                ‹ Prev
              </button>
              {/* Page number buttons (show up to 5 around current page) */}
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const start = Math.max(1, Math.min(page - 2, totalPages - 4));
                return start + i;
              })
                .filter((p) => p >= 1 && p <= totalPages)
                .map((p) => (
                  <button
                    key={p}
                    className={`pagination-btn${p === page ? ' active' : ''}`}
                    onClick={() => setPage(p)}
                  >
                    {p}
                  </button>
                ))}
              <button
                className="pagination-btn"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next ›
              </button>
              <button
                className="pagination-btn"
                onClick={() => setPage(totalPages)}
                disabled={page === totalPages}
              >
                »
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default TicketList;
