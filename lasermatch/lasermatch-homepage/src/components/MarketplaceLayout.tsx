import React, { useState } from 'react';
import AdvancedSearch from './AdvancedSearch';
import EquipmentGrid from './EquipmentGrid';
import { useFilters } from '../contexts/FilterContext';

const MarketplaceLayout: React.FC = () => {
  const [showFilters, setShowFilters] = useState(true); // Show filters by default
  const { filters, updateFilter, clearFilters } = useFilters();

  return (
    <div id="marketplace" className="min-h-screen bg-gray-50">
      {/* Advanced Search Component */}
      <AdvancedSearch />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 lg:py-8">
        <div className="flex flex-col lg:flex-row gap-6 lg:gap-8">
          {/* Sidebar Filters - Mobile Toggle */}
          <div className="lg:hidden mb-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-left font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
          </div>

          {/* Sidebar Filters */}
          <div className={`lg:w-80 lg:flex-shrink-0 ${showFilters ? 'block' : 'hidden'}`}>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 lg:p-6 sticky top-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Refine Results</h3>
              
              {/* Search Bar */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">Search Equipment</label>
                <div className="relative">
                  <input
                    type="text"
                    value={filters.keyword || ''}
                    onChange={(e) => updateFilter('keyword', e.target.value)}
                    placeholder="Search for equipment (e.g., 'CO2 laser', 'IPL system', 'fractional')"
                    className="w-full px-4 py-3 text-sm rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary/50 shadow-sm"
                  />
                  <button className="absolute right-2 top-2 bg-primary hover:bg-blue-600 text-white p-1.5 rounded-md transition-colors">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </button>
                </div>
              </div>
              
              {/* Brokered Sales Notice */}
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-blue-900 mb-1">All Sales Are Brokered</h4>
                    <p className="text-xs text-blue-700">
                      Contact our brokers for pricing and detailed information. 
                      No pricing is displayed publicly to ensure fair market value.
                    </p>
                  </div>
                </div>
              </div>

              {/* Equipment Type */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">Equipment Type</label>
                <div className="space-y-2">
                  {['CO2 Lasers', 'IPL Systems', 'RF Devices', 'Ultrasound', 'LED Therapy'].map((type) => (
                    <label key={type} className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={filters.category.includes(type)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            updateFilter('category', [...filters.category, type]);
                          } else {
                            updateFilter('category', filters.category.filter(cat => cat !== type));
                          }
                        }}
                        className="rounded border-gray-300 text-primary focus:ring-primary/50"
                      />
                      <span className="text-sm text-gray-700">{type}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Condition */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">Condition</label>
                <div className="space-y-2">
                  {['New', 'Like New', 'Excellent', 'Very Good', 'Good', 'Fair'].map((condition) => (
                    <label key={condition} className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={filters.condition.includes(condition)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            updateFilter('condition', [...filters.condition, condition]);
                          } else {
                            updateFilter('condition', filters.condition.filter(cond => cond !== condition));
                          }
                        }}
                        className="rounded border-gray-300 text-primary focus:ring-primary/50"
                      />
                      <span className="text-sm text-gray-700">{condition}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Brand */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">Brand</label>
                <div className="space-y-2">
                  {['Lumenis', 'Candela', 'Cutera', 'Cynosure', 'Sciton', 'Alma'].map((brand) => (
                    <label key={brand} className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={filters.brand.includes(brand)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            updateFilter('brand', [...filters.brand, brand]);
                          } else {
                            updateFilter('brand', filters.brand.filter(b => b !== brand));
                          }
                        }}
                        className="rounded border-gray-300 text-primary focus:ring-primary/50"
                      />
                      <span className="text-sm text-gray-700">{brand}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Location */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">Location</label>
                <input
                  type="text"
                  value={filters.location}
                  onChange={(e) => updateFilter('location', e.target.value)}
                  placeholder="City, State or ZIP"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                <div className="mt-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      className="rounded border-gray-300 text-primary focus:ring-primary/50"
                    />
                    <span className="text-sm text-gray-700">Include remote locations</span>
                  </label>
                </div>
              </div>

              {/* Additional Filters */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">Additional Features</label>
                <div className="space-y-2">
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={filters.warranty}
                      onChange={(e) => updateFilter('warranty', e.target.checked)}
                      className="rounded border-gray-300 text-primary focus:ring-primary/50"
                    />
                    <span className="text-sm text-gray-700">Under Warranty</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={filters.inspectionReport}
                      onChange={(e) => updateFilter('inspectionReport', e.target.checked)}
                      className="rounded border-gray-300 text-primary focus:ring-primary/50"
                    />
                    <span className="text-sm text-gray-700">Inspection Report</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      className="rounded border-gray-300 text-primary focus:ring-primary/50"
                    />
                    <span className="text-sm text-gray-700">Free Shipping</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      className="rounded border-gray-300 text-primary focus:ring-primary/50"
                    />
                    <span className="text-sm text-gray-700">Local Pickup Available</span>
                  </label>
                </div>
              </div>

              {/* Clear Filters */}
              <button 
                onClick={clearFilters}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Clear All Filters
              </button>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="flex-1">
            <EquipmentGrid />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketplaceLayout;
