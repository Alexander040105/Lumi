import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchableSelect from '../shared/SearchableSelect';

const items = [
  { id: 1, name: 'Alpha' },
  { id: 2, name: 'Beta' },
];

function setup(overrides = {}) {
  const props = {
    query: '',
    onQueryChange: vi.fn(),
    open: true,
    onOpenChange: vi.fn(),
    items,
    getOptionId: (i) => i.id,
    getOptionLabel: (i) => i.name,
    selectedId: '',
    onSelect: vi.fn(),
    placeholder: 'Pick one',
    emptyText: 'Nothing here',
    moreResultsText: (count, total) => `${count} more of ${total}`,
    ...overrides,
  };
  render(<SearchableSelect {...props} />);
  return props;
}

describe('SearchableSelect', () => {
  it('renders options via getOptionLabel', () => {
    setup();
    expect(screen.getByText('Alpha')).toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
  });

  it('fires onQueryChange when typing', () => {
    const props = setup();
    fireEvent.change(screen.getByPlaceholderText('Pick one'), { target: { value: 'al' } });
    expect(props.onQueryChange).toHaveBeenCalledWith('al');
  });

  it('fires onSelect with the clicked item', () => {
    const props = setup();
    fireEvent.click(screen.getByText('Beta'));
    expect(props.onSelect).toHaveBeenCalledWith(items[1]);
  });

  it('renders moreResultsText when items exceed maxVisible', () => {
    const many = Array.from({ length: 5 }, (_, i) => ({ id: i, name: `Item ${i}` }));
    setup({ items: many, maxVisible: 3 });
    expect(screen.getByText('2 more of 5')).toBeInTheDocument();
  });

  it('renders emptyText when there are no items', () => {
    setup({ items: [] });
    expect(screen.getByText('Nothing here')).toBeInTheDocument();
  });
});
