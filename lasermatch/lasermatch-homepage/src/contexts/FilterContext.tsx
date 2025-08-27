import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

export interface SearchFilters {
  keyword: string;
  category: string[];
  brand: string[];
  priceRange: [number, number];
  condition: string[];
  location: string;
  distance: number;
  yearRange: [number, number];
  features: string[];
  warranty: boolean;
  inspectionReport: boolean;
  sortBy: 'date' | 'price' | 'condition' | 'distance';
  viewMode: 'grid' | 'list';
}

interface FilterContextType {
  filters: SearchFilters;
  updateFilter: (key: keyof SearchFilters, value: any) => void;
  clearFilters: () => void;
  applyFilters: () => void;
  isFiltered: boolean;
}

const defaultFilters: SearchFilters = {
  keyword: '',
  category: [],
  brand: [],
  priceRange: [0, 200000],
  condition: [],
  location: '',
  distance: 100,
  yearRange: [2010, 2024],
  features: [],
  warranty: false,
  inspectionReport: false,
  sortBy: 'date',
  viewMode: 'grid'
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};

interface FilterProviderProps {
  children: ReactNode;
}

export const FilterProvider: React.FC<FilterProviderProps> = ({ children }) => {
  const [filters, setFilters] = useState<SearchFilters>(defaultFilters);

  const updateFilter = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters(defaultFilters);
  };

  const applyFilters = () => {
    // This will trigger a re-render of components that use the filters
    setFilters(prev => ({ ...prev }));
  };

  const isFiltered = () => {
    return (
      filters.keyword !== '' ||
      filters.category.length > 0 ||
      filters.brand.length > 0 ||
      filters.priceRange[0] !== 0 ||
      filters.priceRange[1] !== 200000 ||
      filters.condition.length > 0 ||
      filters.location !== '' ||
      filters.distance !== 100 ||
      filters.yearRange[0] !== 2010 ||
      filters.yearRange[1] !== 2024 ||
      filters.features.length > 0 ||
      filters.warranty ||
      filters.inspectionReport
    );
  };

  const value: FilterContextType = {
    filters,
    updateFilter,
    clearFilters,
    applyFilters,
    isFiltered: isFiltered()
  };

  return (
    <FilterContext.Provider value={value}>
      {children}
    </FilterContext.Provider>
  );
};
