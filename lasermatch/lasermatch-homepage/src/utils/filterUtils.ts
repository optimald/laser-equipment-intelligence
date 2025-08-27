import type { SearchFilters } from '../contexts/FilterContext';

export interface EquipmentItem {
  id: string;
  name: string;
  brand: string;
  model: string;
  type: string;
  year: number;
  condition: string;
  price: number;
  location: string;
  seller: {
    name: string;
    verified: boolean;
    rating: number;
    location: string;
  };
  images: string[];
  description: string;
  specifications: {
    power?: string;
    wavelength?: string;
    applications?: string[];
  };
  features: string[];
  warranty: string;
  shipping: string;
  inspectionReport?: boolean;
}

export const filterEquipment = (equipment: EquipmentItem[], filters: SearchFilters): EquipmentItem[] => {
  return equipment.filter(item => {
    // Keyword search
    if (filters.keyword && filters.keyword.trim() !== '') {
      const searchTerm = filters.keyword.toLowerCase();
      const searchableText = [
        item.name.toLowerCase(),
        item.brand.toLowerCase(),
        item.model.toLowerCase(),
        item.type.toLowerCase(),
        item.description.toLowerCase()
      ].join(' ');
      
      if (!searchableText.includes(searchTerm)) {
        return false;
      }
    }

    // Category filter
    if (filters.category.length > 0) {
      if (!filters.category.some(cat => 
        item.type.toLowerCase().includes(cat.toLowerCase()) ||
        item.description.toLowerCase().includes(cat.toLowerCase())
      )) {
        return false;
      }
    }

    // Brand filter
    if (filters.brand.length > 0) {
      if (!filters.brand.some(brand => 
        item.brand.toLowerCase() === brand.toLowerCase()
      )) {
        return false;
      }
    }

    // Price range filter
    if (filters.priceRange[0] > 0 || filters.priceRange[1] < 200000) {
      if (item.price < filters.priceRange[0] || item.price > filters.priceRange[1]) {
        return false;
      }
    }

    // Condition filter
    if (filters.condition.length > 0) {
      if (!filters.condition.some(cond => 
        item.condition.toLowerCase() === cond.toLowerCase()
      )) {
        return false;
      }
    }

    // Location filter
    if (filters.location && filters.location.trim() !== '') {
      const locationTerm = filters.location.toLowerCase();
      if (!item.location.toLowerCase().includes(locationTerm) &&
          !item.seller.location.toLowerCase().includes(locationTerm)) {
        return false;
      }
    }

    // Year range filter
    if (filters.yearRange[0] > 2010 || filters.yearRange[1] < 2024) {
      if (item.year < filters.yearRange[0] || item.year > filters.yearRange[1]) {
        return false;
      }
    }

    // Features filter
    if (filters.features.length > 0) {
      if (!filters.features.some(feature => 
        item.features.some(itemFeature => 
          itemFeature.toLowerCase().includes(feature.toLowerCase())
        )
      )) {
        return false;
      }
    }

    // Warranty filter
    if (filters.warranty) {
      if (!item.warranty.toLowerCase().includes('remaining') && 
          !item.warranty.toLowerCase().includes('valid')) {
        return false;
      }
    }

    // Inspection report filter
    if (filters.inspectionReport) {
      if (!item.inspectionReport) {
        return false;
      }
    }

    return true;
  });
};

export const sortEquipment = (equipment: EquipmentItem[], sortBy: string): EquipmentItem[] => {
  const sorted = [...equipment];
  
  switch (sortBy) {
    case 'price':
      return sorted.sort((a, b) => a.price - b.price);
    case 'price-desc':
      return sorted.sort((a, b) => b.price - a.price);
    case 'date':
      return sorted.sort((a, b) => b.year - a.year);
    case 'condition':
      const conditionOrder = ['New', 'Like New', 'Excellent', 'Very Good', 'Good', 'Fair'];
      return sorted.sort((a, b) => {
        const aIndex = conditionOrder.indexOf(a.condition);
        const bIndex = conditionOrder.indexOf(b.condition);
        return aIndex - bIndex;
      });
    case 'distance':
      // For now, just sort by location alphabetically
      return sorted.sort((a, b) => a.location.localeCompare(b.location));
    default:
      return sorted;
  }
};

export const getFilteredAndSortedEquipment = (
  equipment: EquipmentItem[], 
  filters: SearchFilters
): EquipmentItem[] => {
  const filtered = filterEquipment(equipment, filters);
  return sortEquipment(filtered, filters.sortBy);
};
