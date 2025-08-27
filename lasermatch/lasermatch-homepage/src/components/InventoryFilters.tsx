import React, { useState } from 'react';

const InventoryFilters: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const brands = ['Aerolase', 'Candela', 'Cutera', 'Lumenis', 'Cynosure', 'Sciton', 'All'];
  const conditions = ['Like New', 'Excellent', 'Very Good', 'Good', 'Fair', 'All'];
  const equipmentTypes = ['Laser', 'IPL', 'RF', 'Ultrasound', 'All'];
  const priceRanges = ['Under $10K', '$10K-$25K', '$25K-$50K', '$50K-$100K', '$100K+', 'All'];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-secondary">Filter Equipment</h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-primary hover:text-blue-600 font-medium text-sm"
        >
          {isExpanded ? 'Hide Filters' : 'Show Filters'}
        </button>
      </div>

      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Brand Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Brand</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50">
              {brands.map((brand) => (
                <option key={brand} value={brand}>{brand}</option>
              ))}
            </select>
          </div>

          {/* Price Range Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50">
              {priceRanges.map((range) => (
                <option key={range} value={range}>{range}</option>
              ))}
            </select>
          </div>

          {/* Condition Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Condition</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50">
              {conditions.map((condition) => (
                <option key={condition} value={condition}>{condition}</option>
              ))}
            </select>
          </div>

          {/* Equipment Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Equipment Type</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50">
              {equipmentTypes.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Quick Filter Tags */}
      <div className="flex flex-wrap gap-2 mt-4">
        <span className="text-sm text-gray-600">Quick filters:</span>
        <button className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full hover:bg-blue-200 transition-colors">
          Recently Added
        </button>
        <button className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full hover:bg-green-200 transition-colors">
          Price Reduced
        </button>
        <button className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full hover:bg-purple-200 transition-colors">
          Free Shipping
        </button>
        <button className="px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full hover:bg-orange-200 transition-colors">
          Under Warranty
        </button>
      </div>
    </div>
  );
};

export default InventoryFilters;
