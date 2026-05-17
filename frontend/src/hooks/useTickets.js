/**
 * hooks/useTickets.js — Custom hook for fetching paginated ticket lists.
 *
 * Manages: loading state, error state, pagination, and data refresh.
 */

import { useState, useEffect, useCallback } from 'react';
import ticketService from '../services/ticketService';

function useTickets(initialPage = 1, initialPageSize = 20) {
  const [tickets, setTickets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialPage);
  const [pageSize] = useState(initialPageSize);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ticketService.getAll(page, pageSize);
      setTickets(data.tickets);
      setTotal(data.total);
    } catch (err) {
      setError(err.message || 'Failed to load tickets.');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize]);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  return {
    tickets,
    total,
    page,
    pageSize,
    loading,
    error,
    setPage,
    refetch: fetchTickets,
  };
}

export default useTickets;
