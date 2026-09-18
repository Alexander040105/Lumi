import { describe, it, expect } from 'vitest';
import { filterMunicipalities, formatMunicipalityLabel, nearestMunicipality } from './municipalities';

const items = [
  { municipality_id: 1, name: 'Burgos', province_name: 'Ilocos Norte' },
  { municipality_id: 2, name: 'Burgos', province_name: 'Pangasinan' },
  { municipality_id: 3, name: 'Calamba', province_name: 'Laguna' },
  { municipality_id: 4, name: 'Santa Rosa', province_name: 'Laguna' },
  { municipality_id: 5, name: 'San Burgos', province_name: 'Cavite' },
  { municipality_id: 6, name: 'Mabini', province_name: 'Batangas' },
  { municipality_id: 7, name: 'Laguna Vista', province_name: 'Batangas' },
];

const ids = (list) => list.map((m) => m.municipality_id);

describe('filterMunicipalities', () => {
  it('returns all items for an empty or blank query', () => {
    expect(filterMunicipalities(items, '')).toBe(items);
    expect(filterMunicipalities(items, '   ')).toHaveLength(7);
  });

  it('is case-insensitive', () => {
    expect(ids(filterMunicipalities(items, 'BURGOS'))).toEqual([1, 2, 5]);
  });

  it('ranks startsWith matches before name-substring matches', () => {
    expect(ids(filterMunicipalities(items, 'burg'))).toEqual([1, 2, 5]);
  });

  it('breaks ties alphabetically by name', () => {
    expect(ids(filterMunicipalities(items, 'san'))).toEqual([5, 4]);
  });

  it('ranks province-only matches after name matches', () => {
    expect(ids(filterMunicipalities(items, 'laguna'))).toEqual([7, 3, 4]);
  });

  it('returns an empty list when nothing matches', () => {
    expect(filterMunicipalities(items, 'zzz')).toEqual([]);
  });
});

describe('formatMunicipalityLabel', () => {
  it('joins name and province when present', () => {
    expect(formatMunicipalityLabel(items[0])).toBe('Burgos, Ilocos Norte');
  });

  it('returns just the name without a province', () => {
    expect(formatMunicipalityLabel({ name: 'Solo' })).toBe('Solo');
  });
});

describe('nearestMunicipality', () => {
  // Manila ~14.60, 120.98; Calamba, Laguna ~14.21, 121.16; Baguio ~16.40, 120.60
  const withCoords = [
    { municipality_id: 10, name: 'Manila', lat: 14.5995, lon: 120.9842 },
    { municipality_id: 11, name: 'Calamba', lat: 14.2116, lon: 121.1653 },
    { municipality_id: 12, name: 'Baguio', lat: 16.4023, lon: 120.596 },
    { municipality_id: 13, name: 'NoCoords', lat: null, lon: null },
    { municipality_id: 14, name: 'BadCoords' },
  ];

  it('returns the closest municipality', () => {
    const result = nearestMunicipality(withCoords, 14.25, 121.15);
    expect(result.item.municipality_id).toBe(11);
    expect(result.distanceKm).toBeLessThan(10);
  });

  it('reports an approximate distance', () => {
    // Manila → Calamba is roughly 50 km as the crow flies
    const result = nearestMunicipality(withCoords, 14.5995, 120.9842);
    expect(result.item.municipality_id).toBe(10);
    expect(result.distanceKm).toBeLessThan(1);
  });

  it('skips entries with missing or invalid coordinates', () => {
    const sparse = [
      { municipality_id: 20, name: 'Far', lat: 16.4, lon: 120.6 },
      { municipality_id: 21, name: 'Null' },
      { municipality_id: 22, name: 'NaN', lat: 'x', lon: 'y' },
    ];
    expect(nearestMunicipality(sparse, 16.4, 120.6).item.municipality_id).toBe(20);
  });

  it('returns null when nothing has coordinates', () => {
    expect(nearestMunicipality([{ name: 'A' }, { name: 'B', lat: null }], 14, 121)).toBeNull();
    expect(nearestMunicipality([], 14, 121)).toBeNull();
    expect(nearestMunicipality(null, 14, 121)).toBeNull();
  });

  it('returns null for invalid input coordinates', () => {
    expect(nearestMunicipality(withCoords, NaN, 121)).toBeNull();
    expect(nearestMunicipality(withCoords, 14, undefined)).toBeNull();
  });
});
