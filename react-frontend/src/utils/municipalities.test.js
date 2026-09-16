import { describe, it, expect } from 'vitest';
import { filterMunicipalities, formatMunicipalityLabel } from './municipalities';

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
