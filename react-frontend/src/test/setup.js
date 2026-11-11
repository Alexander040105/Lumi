import '@testing-library/jest-dom/vitest';

// jsdom@25 does not surface localStorage/sessionStorage through vitest's
// populateGlobal, so code reading window.localStorage crashes in tests.
// Provide a minimal in-memory Storage when it is missing.
class MemoryStorage {
  #map = new Map();
  get length() {
    return this.#map.size;
  }
  key(index) {
    return [...this.#map.keys()][index] ?? null;
  }
  getItem(key) {
    return this.#map.has(key) ? this.#map.get(key) : null;
  }
  setItem(key, value) {
    this.#map.set(String(key), String(value));
  }
  removeItem(key) {
    this.#map.delete(key);
  }
  clear() {
    this.#map.clear();
  }
}

for (const name of ['localStorage', 'sessionStorage']) {
  if (typeof window !== 'undefined' && !window[name]) {
    Object.defineProperty(window, name, {
      value: new MemoryStorage(),
      configurable: true,
    });
  }
}
