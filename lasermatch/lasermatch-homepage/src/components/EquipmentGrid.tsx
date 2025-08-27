import React, { useState, useEffect } from 'react';
import { useFilters } from '../contexts/FilterContext';
import { getFilteredAndSortedEquipment } from '../utils/filterUtils';
import type { EquipmentItem } from '../utils/filterUtils';
import laserImage from '../assets/laser.png';

const EquipmentGrid: React.FC = () => {
  const { filters, updateFilter } = useFilters();
  const [filteredEquipment, setFilteredEquipment] = useState<EquipmentItem[]>([]);

  // Sample equipment data - replace with real API data
  const allEquipmentItems: EquipmentItem[] = [
    {
      id: '1',
      name: 'UltraPulse Encore CO2 Laser',
      brand: 'Lumenis',
      model: 'UltraPulse Encore',
      type: 'CO2 Laser',
      year: 2020,
      condition: 'Excellent',
      price: 45000,
      location: 'New York, NY',
      seller: {
        name: 'Advanced Aesthetics Center',
        verified: true,
        rating: 4.8,
        location: 'New York, NY'
      },
      images: [
        laserImage
      ],
      description: 'Professional CO2 laser system for skin resurfacing, scar treatment, and wrinkle reduction.',
      specifications: {
        power: '60W',
        wavelength: '10,600nm',
        applications: ['Skin Resurfacing', 'Scar Treatment', 'Wrinkle Reduction', 'Acne Scars']
      },
      features: ['Fractional & Ablative modes', 'SmartScan technology', 'Integrated cooling', 'Touch screen interface'],
      warranty: '6 months remaining',
      shipping: 'Free shipping',
      inspectionReport: true
    },
    {
      id: '2',
      name: 'GentleMax Pro Laser System',
      brand: 'Candela',
      model: 'GentleMax Pro',
      type: 'Alexandrite & Nd:YAG',
      year: 2021,
      condition: 'Like New',
      price: 65000,
      location: 'Los Angeles, CA',
      seller: {
        name: 'Elite Medical Spa',
        verified: true,
        rating: 4.9,
        location: 'Los Angeles, CA'
      },
      images: [
        laserImage
      ],
      description: 'Dual-wavelength laser system for hair removal, vascular lesions, and pigmentation.',
      specifications: {
        power: '100W',
        wavelength: '755nm & 1064nm',
        applications: ['Hair Removal', 'Vascular Lesions', 'Pigmentation', 'Skin Tightening']
      },
      features: ['Dual wavelength', 'Dynamic cooling', 'Large spot sizes', 'Fast treatment'],
      warranty: '12 months remaining',
      shipping: 'Local pickup available',
      inspectionReport: true
    },
    {
      id: '3',
      name: 'Excel V+ Vascular Laser',
      brand: 'Cutera',
      model: 'Excel V+',
      type: 'KTP Laser',
      year: 2022,
      condition: 'Excellent',
      price: 35000,
      location: 'Miami, FL',
      seller: {
        name: 'Beauty & Wellness Clinic',
        verified: true,
        rating: 4.7,
        location: 'Miami, FL'
      },
      images: [
        laserImage
      ],
      description: 'Advanced KTP laser for vascular lesions, rosacea, and skin rejuvenation.',
      specifications: {
        power: '30W',
        wavelength: '532nm',
        applications: ['Vascular Lesions', 'Rosacea', 'Skin Rejuvenation', 'Pigmentation']
      },
      features: ['KTP technology', 'Variable pulse width', 'Cooling system', 'Portable design'],
      warranty: '18 months remaining',
      shipping: 'Free shipping',
      inspectionReport: false
    }
  ];



  // Apply filters whenever filters change
  useEffect(() => {
    const filtered = getFilteredAndSortedEquipment(allEquipmentItems, filters);
    setFilteredEquipment(filtered);
  }, [filters, allEquipmentItems]);

  const getConditionColor = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'like new': return 'bg-green-100 text-green-800';
      case 'excellent': return 'bg-blue-100 text-blue-800';
      case 'very good': return 'bg-purple-100 text-purple-800';
      case 'good': return 'bg-yellow-100 text-yellow-800';
      case 'fair': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header Controls */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
                      <h1 className="text-2xl font-bold text-gray-900">⚡ Equipment Available</h1>
        <p className="text-gray-600 mt-1">Browse {filteredEquipment.length} verified pieces of equipment from our network</p>
            </div>
            
            <div className="flex items-center gap-4">
              {/* View Mode Toggle */}
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => updateFilter('viewMode', 'grid')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    filters.viewMode === 'grid' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Grid
                </button>
                <button
                  onClick={() => updateFilter('viewMode', 'list')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    filters.viewMode === 'list' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  List
                </button>
              </div>

              {/* Sort Dropdown */}
              <select
                value={filters.sortBy}
                onChange={(e) => updateFilter('sortBy', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="date">Newest First</option>
                <option value="price">Price: Low to High</option>
                <option value="price-desc">Price: High to Low</option>
                <option value="condition">Best Condition</option>
                <option value="distance">Nearest First</option>
              </select>
            </div>
          </div>
        </div>
      </div>

              {/* Equipment Grid */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 lg:py-8">
          <div className={`grid gap-4 sm:gap-6 ${
            filters.viewMode === 'grid' 
              ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3' 
              : 'grid-cols-1'
          }`}>
            {filteredEquipment.map((item) => (
              <div
                key={item.id}
                className={`bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 ${
                  filters.viewMode === 'list' ? 'flex flex-col sm:flex-row' : ''
                }`}
              >
                {/* Image Section */}
                <div className={`relative equipment-image-container ${filters.viewMode === 'list' ? 'sm:w-48 sm:flex-shrink-0' : ''}`}>
                  <img
                    src={item.images[0]}
                    alt={item.name}
                    className={`equipment-image ${
                      filters.viewMode === 'list' 
                        ? 'h-48 sm:h-48 sm:w-48' 
                        : 'h-64 w-full'
                    }`}
                  />
                  <div className="absolute top-2 left-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConditionColor(item.condition)}`}>
                      {item.condition}
                    </span>
                  </div>
                  <div className="absolute top-2 right-2">
                    <button className="p-1.5 bg-white/90 hover:bg-white rounded-full shadow-md transition-colors">
                      <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    </button>
                  </div>
                  {item.inspectionReport && (
                    <div className="absolute bottom-2 left-2">
                      <span className="px-2 py-1 bg-green-500 text-white text-xs font-medium rounded-full">
                        ✓ Inspected
                      </span>
                    </div>
                  )}
                </div>

                {/* Content Section */}
                <div className={`p-4 sm:p-6 ${filters.viewMode === 'list' ? 'flex-1 flex flex-col' : ''}`}>
                  {/* Equipment Info */}
                  <div className="mb-3 sm:mb-4">
                    <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-1 sm:mb-2 line-clamp-2">
                      {item.brand} {item.model}
                    </h3>
                    <p className="text-sm text-gray-600 mb-1 sm:mb-2">{item.type}</p>
                    <div className="flex items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-500">
                      <span>{item.year}</span>
                      <span>•</span>
                      <span>{item.location}</span>
                    </div>
                  </div>

                  {/* Brokered Notice */}
                  <div className="mb-3 sm:mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="text-center">
                      <div className="text-sm font-medium text-blue-900 mb-1">Contact Broker for Pricing</div>
                      <div className="text-xs text-blue-700">All sales are brokered through LaserMatch</div>
                    </div>
                  </div>

                  {/* Verification Badge */}
                  <div className="mb-3 sm:mb-4 flex justify-center">
                    <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                      ✓ Verified Equipment
                    </span>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 mb-3 sm:mb-4">
                    <button className="flex-1 bg-primary hover:bg-blue-600 text-white font-semibold py-2 sm:py-3 px-3 sm:px-4 rounded-lg transition-colors text-sm">
                      Contact Broker
                    </button>
                    <button className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 sm:py-3 px-3 sm:px-4 rounded-lg transition-colors text-sm">
                      Get Details
                    </button>
                  </div>

                  {/* Quick Specs */}
                  <div className="mt-auto pt-3 sm:pt-4 border-t border-gray-100">
                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                      {item.specifications.power && (
                        <div>Power: {item.specifications.power}</div>
                      )}
                      {item.specifications.wavelength && (
                        <div>Wavelength: {item.specifications.wavelength}</div>
                      )}
                      <div>Year: {item.year}</div>
                      <div>Condition: {item.condition}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

        {/* Load More */}
        <div className="text-center mt-12">
          <button className="bg-white hover:bg-gray-50 text-gray-700 font-medium py-3 px-8 rounded-lg border border-gray-300 transition-colors">
            Load More Equipment
          </button>
        </div>
      </div>
    </div>
  );
};

export default EquipmentGrid;
