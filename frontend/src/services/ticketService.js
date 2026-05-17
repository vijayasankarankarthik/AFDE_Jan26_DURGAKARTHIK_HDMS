/**
 * services/ticketService.js — All API calls related to the ticket resource.
 *
 * Each function returns the relevant data or throws a normalised error.
 * Components / hooks should import from here — never call axios directly.
 */

import api from '../api';

const BASE = '/api/tickets';

const ticketService = {
  /**
   * Fetch all tickets with optional pagination.
   * @param {number} page      1-based page number
   * @param {number} pageSize  Results per page
   * @returns {Promise<{total, page, page_size, tickets}>}
   */
  getAll: async (page = 1, pageSize = 20) => {
    const response = await api.get(BASE, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  /**
   * Fetch a single ticket by ID.
   * @param {number|string} id
   * @returns {Promise<Ticket>}
   */
  getById: async (id) => {
    const response = await api.get(`${BASE}/${id}`);
    return response.data;
  },

  /**
   * Create a new ticket.
   * @param {Object} payload  TicketCreate shape
   * @returns {Promise<Ticket>}
   */
  create: async (payload) => {
    const response = await api.post(BASE, payload);
    return response.data;
  },

  /**
   * Update an existing ticket (partial update).
   * @param {number|string} id
   * @param {Object} payload  TicketUpdate shape
   * @returns {Promise<Ticket>}
   */
  update: async (id, payload) => {
    const response = await api.put(`${BASE}/${id}`, payload);
    return response.data;
  },

  /**
   * Delete a ticket by ID.
   * @param {number|string} id
   * @returns {Promise<{message, ticket_id}>}
   */
  remove: async (id) => {
    const response = await api.delete(`${BASE}/${id}`);
    return response.data;
  },

  /**
   * Search / filter tickets.
   * @param {Object} params  { q, status, priority, category, department, page, page_size }
   * @returns {Promise<{total, page, page_size, tickets}>}
   */
  search: async (params) => {
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== '' && v !== null && v !== undefined)
    );
    const response = await api.get(`${BASE}/search`, { params: cleanParams });
    return response.data;
  },

  /**
   * Fetch dashboard statistics.
   * @returns {Promise<TicketStats>}
   */
  getStats: async () => {
    const response = await api.get(`${BASE}/stats`);
    return response.data;
  },
};

export default ticketService;
