'use client'

import { useState, useEffect } from 'react'
import { ArrowPathIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'

interface LaserMatchItem {
  id: string
  title: string
  brand?: string
  model?: string
  condition?: string
  price?: number
  location?: string
  description?: string
  images?: string[]
  url: string
  sources?: {
    source: string
    url: string
    price?: number
    found: boolean
  }[]
  searchStatus?: 'idle' | 'searching' | 'completed' | 'error'
}

export default function LaserMatchTab() {
  const [items, setItems] = useState<LaserMatchItem[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Fetch LaserMatch items on component mount
  useEffect(() => {
    fetchLaserMatchItems()
  }, [])

  const fetchLaserMatchItems = async () => {
    setIsLoading(true)
    try {
      const { apiService } = await import('../services/api')
      const results = await apiService.searchEquipment({ sources: ['LaserMatch.io'] })
      // Convert API results to component interface
      const convertedResults: LaserMatchItem[] = results.map(item => ({
        id: item.id.toString(),
        title: item.title,
        brand: item.brand,
        model: item.model,
        condition: item.condition,
        price: item.price,
        location: item.location,
        description: item.description,
        images: item.images,
        url: item.url || '',
        sources: []
      }))
      setItems(convertedResults)
    } catch (error) {
      console.error('Failed to fetch LaserMatch items:', error)
      // Fallback to mock data
      const mockItems: LaserMatchItem[] = [
        {
          id: '1',
          title: 'Sciton Joule Laser System',
          brand: 'Sciton',
          model: 'Joule',
          condition: 'excellent',
          price: 85000,
          location: 'California, USA',
          description: 'Complete Sciton Joule laser system with multiple handpieces',
          url: 'https://lasermatch.io/item/1',
          sources: []
        },
        {
          id: '2',
          title: 'Cynosure PicoSure Pro',
          brand: 'Cynosure',
          model: 'PicoSure Pro',
          condition: 'good',
          price: 120000,
          location: 'Texas, USA',
          description: 'Cynosure PicoSure Pro tattoo removal laser',
          url: 'https://lasermatch.io/item/2',
          sources: []
        },
        {
          id: '3',
          title: 'Cutera Excel V System',
          brand: 'Cutera',
          model: 'Excel V',
          condition: 'excellent',
          price: 95000,
          location: 'Florida, USA',
          description: 'Cutera Excel V laser system for aesthetic treatments',
          url: 'https://lasermatch.io/item/3',
          sources: []
        }
      ]
      setItems(mockItems)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshLaserMatchItems = async () => {
    setIsRefreshing(true)
    try {
      // Run the lasermatch spider
      const { apiService } = await import('../services/api')
      await apiService.runSpider('lasermatch')
      
      // Wait a moment for the spider to complete, then refresh the items
      setTimeout(() => {
        fetchLaserMatchItems()
      }, 5000)
    } catch (error) {
      console.error('Failed to refresh LaserMatch items:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const findSources = async (item: LaserMatchItem) => {
    // Update item status to searching
    setItems(prev => prev.map(i => 
      i.id === item.id 
        ? { ...i, searchStatus: 'searching' as const }
        : i
    ))

    try {
      const { apiService } = await import('../services/api')
      
      // Search for this item across all configured sources
      const searchResults = await apiService.searchEquipment({
        query: item.title,
        brand: item.brand,
        model: item.model
      })

      // Filter out the original LaserMatch item and format sources
      const sources = searchResults
        .filter(result => result.source !== 'LaserMatch.io')
        .map(result => ({
          source: result.source,
          url: result.url || '',
          price: result.price,
          found: true
        }))

      // Update item with found sources
      setItems(prev => prev.map(i => 
        i.id === item.id 
          ? { 
              ...i, 
              sources,
              searchStatus: 'completed' as const
            }
          : i
      ))
    } catch (error) {
      console.error('Failed to find sources:', error)
      setItems(prev => prev.map(i => 
        i.id === item.id 
          ? { ...i, searchStatus: 'error' as const }
          : i
      ))
    }
  }

  const formatPrice = (price?: number) => {
    if (!price) return 'Price not available'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading LaserMatch items...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Refresh Button */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">LaserMatch Items</h2>
          <p className="text-gray-600">Found {items.length} items from LaserMatch.io</p>
        </div>
        <button
          onClick={refreshLaserMatchItems}
          disabled={isRefreshing}
          className="btn-primary flex items-center"
        >
          <ArrowPathIcon className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? 'Refreshing...' : 'Refresh Items'}
        </button>
      </div>

      {/* Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((item) => (
          <div key={item.id} className="card">
            {/* Item Image */}
            <div className="aspect-w-16 aspect-h-9 mb-4">
              <div className="w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center">
                {item.images && item.images.length > 0 ? (
                  <img 
                    src={item.images[0]} 
                    alt={item.title}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <div className="text-gray-400 text-center">
                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="mt-2 text-sm">No image available</p>
                  </div>
                )}
              </div>
            </div>

            {/* Item Details */}
            <div className="space-y-3">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                  {item.title}
                </h3>
                {(item.brand || item.model) && (
                  <p className="text-sm text-gray-600">
                    {item.brand} {item.model}
                  </p>
                )}
              </div>

              <div className="flex justify-between items-center">
                <span className="text-lg font-bold text-primary-600">
                  {formatPrice(item.price)}
                </span>
                {item.condition && (
                  <span className="badge badge-success">
                    {item.condition}
                  </span>
                )}
              </div>

              {item.location && (
                <p className="text-sm text-gray-500">
                  📍 {item.location}
                </p>
              )}

              {item.description && (
                <p className="text-sm text-gray-600 line-clamp-3">
                  {item.description}
                </p>
              )}

              {/* Find Sources Button */}
              <button
                onClick={() => findSources(item)}
                disabled={item.searchStatus === 'searching'}
                className="w-full btn-secondary flex items-center justify-center"
              >
                <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                {item.searchStatus === 'searching' ? 'Searching...' : 'Find Sources'}
              </button>

              {/* Search Status */}
              {item.searchStatus === 'searching' && (
                <div className="text-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                  <p className="text-sm text-gray-500 mt-2">Searching sources...</p>
                </div>
              )}

              {/* Found Sources */}
              {item.sources && item.sources.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-900">
                    Found {item.sources.length} sources:
                  </h4>
                  {item.sources.map((source, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{source.source}</p>
                        {source.price && (
                          <p className="text-sm text-gray-600">{formatPrice(source.price)}</p>
                        )}
                      </div>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 text-sm"
                      >
                        View →
                      </a>
                    </div>
                  ))}
                </div>
              )}

              {/* Error Status */}
              {item.searchStatus === 'error' && (
                <div className="text-center text-red-600 text-sm">
                  ❌ Failed to find sources
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {items.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No items found. Click "Refresh Items" to load LaserMatch items.</p>
        </div>
      )}
    </div>
  )
}
