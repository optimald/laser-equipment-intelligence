'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { SearchIcon, FilterIcon } from '@heroicons/react/24/outline'

interface SearchForm {
  query: string
  brand: string
  model: string
  condition: string
  maxPrice: number
  location: string
  sources: string[]
}

interface EquipmentSearchProps {
  onSearch: (params: SearchForm) => void
  isSearching: boolean
}

export default function EquipmentSearch({ onSearch, isSearching }: EquipmentSearchProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)
  const { register, handleSubmit, watch, reset } = useForm<SearchForm>({
    defaultValues: {
      query: '',
      brand: '',
      model: '',
      condition: 'any',
      maxPrice: 0,
      location: '',
      sources: []
    }
  })

  const onSubmit = (data: SearchForm) => {
    onSearch(data)
  }

  const availableSources = [
    { id: 'lasermatch', name: 'LaserMatch.io', priority: 'HIGH' },
    { id: 'dotmed', name: 'DOTmed Auctions', priority: 'HIGH' },
    { id: 'bidspotter', name: 'BidSpotter', priority: 'HIGH' },
    { id: 'ebay', name: 'eBay', priority: 'MEDIUM' },
    { id: 'govdeals', name: 'GovDeals', priority: 'MEDIUM' },
    { id: 'facebook', name: 'Facebook Marketplace', priority: 'LOW' },
    { id: 'craigslist', name: 'Craigslist', priority: 'LOW' },
    { id: 'thelaserwarehouse', name: 'The Laser Warehouse', priority: 'HIGH' },
    { id: 'laser_agent', name: 'Laser Agent', priority: 'HIGH' },
    { id: 'medwow', name: 'Medwow', priority: 'MEDIUM' },
    { id: 'iron_horse', name: 'Iron Horse Auction', priority: 'HIGH' },
    { id: 'kurtz', name: 'Kurtz Auction', priority: 'HIGH' },
    { id: 'asset_recovery', name: 'Asset Recovery Services', priority: 'HIGH' },
    { id: 'hilditch', name: 'Hilditch Group', priority: 'MEDIUM' },
  ]

  const brands = [
    'Sciton', 'Cynosure', 'Cutera', 'Candela', 'Lumenis', 'Alma', 'InMode',
    'BTL', 'Lutronic', 'Bison', 'Aerolase', 'Quanta', 'Fotona', 'Palomar'
  ]

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Basic Search */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-1">
            Search Equipment
          </label>
          <div className="relative">
            <input
              {...register('query')}
              type="text"
              placeholder="Enter equipment name, model, or keywords..."
              className="input-field pl-10"
            />
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          </div>
        </div>
        
        <div>
          <label htmlFor="brand" className="block text-sm font-medium text-gray-700 mb-1">
            Brand
          </label>
          <select {...register('brand')} className="input-field">
            <option value="">Any Brand</option>
            {brands.map(brand => (
              <option key={brand} value={brand}>{brand}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Advanced Search Toggle */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center text-sm text-primary-600 hover:text-primary-700"
        >
          <FilterIcon className="h-4 w-4 mr-1" />
          {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
        </button>
        
        <div className="flex space-x-3">
          <button
            type="button"
            onClick={() => reset()}
            className="btn-secondary"
          >
            Clear
          </button>
          <button
            type="submit"
            disabled={isSearching}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSearching ? 'Searching...' : 'Search Equipment'}
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
              Model
            </label>
            <input
              {...register('model')}
              type="text"
              placeholder="e.g., Joule, PicoSure, Excel V"
              className="input-field"
            />
          </div>
          
          <div>
            <label htmlFor="condition" className="block text-sm font-medium text-gray-700 mb-1">
              Condition
            </label>
            <select {...register('condition')} className="input-field">
              <option value="any">Any Condition</option>
              <option value="excellent">Excellent</option>
              <option value="good">Good</option>
              <option value="fair">Fair</option>
              <option value="poor">Poor</option>
              <option value="refurbished">Refurbished</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="maxPrice" className="block text-sm font-medium text-gray-700 mb-1">
              Max Price ($)
            </label>
            <input
              {...register('maxPrice', { valueAsNumber: true })}
              type="number"
              placeholder="No limit"
              className="input-field"
            />
          </div>
          
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
              Location
            </label>
            <input
              {...register('location')}
              type="text"
              placeholder="City, State, Country"
              className="input-field"
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Sources
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-32 overflow-y-auto">
              {availableSources.map(source => (
                <label key={source.id} className="flex items-center">
                  <input
                    {...register('sources')}
                    type="checkbox"
                    value={source.id}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    {source.name}
                    <span className={`ml-1 badge ${
                      source.priority === 'HIGH' ? 'badge-error' :
                      source.priority === 'MEDIUM' ? 'badge-warning' :
                      'badge-success'
                    }`}>
                      {source.priority}
                    </span>
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>
      )}
    </form>
  )
}
