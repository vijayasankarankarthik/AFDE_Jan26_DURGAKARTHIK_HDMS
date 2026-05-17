/**
 * hooks/useDebounce.js — Debounce a value by the specified delay (ms).
 *
 * Prevents sending a search API request on every keystroke.
 * Returns the debounced value after the user stops typing.
 *
 * @param {*}      value  The value to debounce (e.g. search query string)
 * @param {number} delay  Debounce delay in milliseconds (default 400ms)
 * @returns {*}           The debounced value
 */

import { useState, useEffect } from 'react';

function useDebounce(value, delay = 400) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

export default useDebounce;
