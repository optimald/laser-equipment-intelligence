'use client'

import { useState, useEffect } from 'react'
import { ArrowPathIcon, MagnifyingGlassIcon, PencilIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface LaserMatchItem {
  id: string
  title: string
  brand?: string
  model?: string
  condition?: string
  price?: number
  location?: string
  description?: string
  url: string
  sources?: {
    source: string
    url: string
    price?: number
    found: boolean
  }[]
  searchStatus?: 'idle' | 'searching' | 'completed' | 'error'
  // Procurement fields
  assignedRep?: string
  targetPrice?: number
  sourcingStatus: 'not_started' | 'in_progress' | 'quoted' | 'negotiating' | 'purchased' | 'declined'
  notes?: string
}

const SOURCING_STATUS_OPTIONS = [
  { value: 'not_started', label: 'Not Started', color: 'bg-gray-100 text-gray-800' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-blue-100 text-blue-800' },
  { value: 'quoted', label: 'Quoted', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'negotiating', label: 'Negotiating', color: 'bg-orange-100 text-orange-800' },
  { value: 'purchased', label: 'Purchased', color: 'bg-green-100 text-green-800' },
  { value: 'declined', label: 'Declined', color: 'bg-red-100 text-red-800' }
]

const REPS = ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Chen', 'Tom Wilson']

// Helper function to extract clean brand name from title
const cleanTitle = (title: string): string => {
  // If title contains a colon, take everything before the first colon
  if (title.includes(':')) {
    const brandPart = title.split(':')[0].trim()
    // Remove any newlines and take just the first line
    return brandPart.split('\n')[0].trim()
  }
  // Otherwise, take the first word
  const words = title.split(' ')
  return words[0] || title
}

export default function LaserMatchTab() {
  const [items, setItems] = useState<LaserMatchItem[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [editingItem, setEditingItem] = useState<string | null>(null)
  const [stats, setStats] = useState<{
    total_items: number
    hot_list_items: number
    in_demand_items: number
    latest_update: string | null
  } | null>(null)

  // Fetch LaserMatch items and stats on component mount
  useEffect(() => {
    fetchLaserMatchItems()
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const { apiService } = await import('../services/api')
      const statsData = await apiService.getLaserMatchStats()
      setStats(statsData)
    } catch (error) {
      console.error('Failed to fetch LaserMatch stats:', error)
    }
  }

  const fetchLaserMatchItems = async () => {
    setIsLoading(true)
    try {
      const { apiService } = await import('../services/api')
      const response = await apiService.getLaserMatchItems(0, 500) // Get up to 500 items
      
      if (!response.items || response.items.length === 0) {
        console.log('No LaserMatch items found in database. Click "Refresh Items" to run the scraper.')
        setItems([])
        return
      }
      
      // Convert API results to component interface
      const convertedResults: LaserMatchItem[] = response.items.map(item => ({
        id: item.id.toString(),
        title: item.title,
        brand: item.brand,
        model: item.model,
        condition: item.condition,
        price: item.price,
        location: item.location,
        description: item.description,
        url: item.url || '',
        sources: [],
        sourcingStatus: 'not_started' as const,
        assignedRep: undefined,
        targetPrice: undefined,
        notes: ''
      }))
      setItems(convertedResults)
    } catch (error) {
      console.error('Failed to fetch LaserMatch items:', error)
      setItems([])
    } finally {
      setIsLoading(false)
    }
  }

  const refreshLaserMatchItems = async () => {
    setIsRefreshing(true)
    try {
      // Run the LaserMatch scraper
      const { apiService } = await import('../services/api')
      const result = await apiService.scrapeLaserMatch()
      
      console.log(`✅ Scraper completed: ${result.items_scraped} items scraped in ${result.execution_time.toFixed(2)}s`)
      
      // Wait a moment for database update, then refresh the items and stats
      setTimeout(() => {
        fetchLaserMatchItems()
        fetchStats()
      }, 2000)
    } catch (error) {
      console.error('Failed to refresh LaserMatch items:', error)
      
      // Show user-friendly error message
      const errorMessage = error instanceof Error ? error.message : String(error)
      if (errorMessage.includes('404') || errorMessage.includes('Not Found')) {
        alert('⚠️ LaserMatch scraper endpoint not available. The backend API may need to be updated with the latest LaserMatch endpoints.')
      } else {
        alert(`❌ Failed to refresh items: ${errorMessage}`)
      }
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

  const updateItem = (itemId: string, updates: Partial<LaserMatchItem>) => {
    setItems(prev => prev.map(item => 
      item.id === itemId ? { ...item, ...updates } : item
    ))
  }

  const formatPrice = (price?: number) => {
    if (!price) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price)
  }

  const getStatusColor = (status: string) => {
    const statusOption = SOURCING_STATUS_OPTIONS.find(opt => opt.value === status)
    return statusOption?.color || 'bg-gray-100 text-gray-800'
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
          <h2 className="text-2xl font-bold text-gray-900">LaserMatch Procurement</h2>
          <p className="text-gray-600">
            {stats ? (
              <>
                Managing {stats.total_items} items from LaserMatch.io
                {stats.latest_update && (
                  <span className="text-sm text-gray-500 ml-2">
                    • Last updated: {new Date(stats.latest_update).toLocaleString()}
                  </span>
                )}
              </>
            ) : (
              `Managing ${items.length} items from LaserMatch.io`
            )}
          </p>
          {stats && (
            <div className="flex space-x-4 text-sm text-gray-500 mt-1">
              <span>🔥 Hot List: {stats.hot_list_items} items</span>
              <span>📈 In Demand: {stats.in_demand_items} items</span>
            </div>
          )}
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

      {/* Items Cards */}
      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
            {/* Main Card Content */}
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                {/* Equipment Info */}
                <div className="flex-1 min-w-0 mr-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2 line-clamp-2">
                    {cleanTitle(item.title)}
                  </h3>
                  <div className="text-sm text-gray-500 mb-1">
                    {cleanTitle(item.brand || '')}
                  </div>
                  <div className="text-xs text-gray-400 mb-3">
                    {item.condition} • {item.location}
                  </div>
                  <div className="text-sm text-gray-600">
                    {item.description}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 flex-shrink-0">
                  {editingItem === item.id ? (
                    <>
                      <button
                        onClick={() => setEditingItem(null)}
                        className="text-green-600 hover:text-green-700 p-2"
                        title="Save"
                      >
                        <CheckIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => setEditingItem(null)}
                        className="text-gray-400 hover:text-gray-600 p-2"
                        title="Cancel"
                      >
                        <XMarkIcon className="h-5 w-5" />
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => findSources(item)}
                        disabled={item.searchStatus === 'searching'}
                        className="text-blue-600 hover:text-blue-700 disabled:text-gray-400 p-2"
                        title="Find Sources"
                      >
                        <MagnifyingGlassIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => setEditingItem(item.id)}
                        className="text-gray-600 hover:text-gray-700 p-2"
                        title="Edit"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* Price and Target Price Side by Side */}
              <div className="grid grid-cols-2 gap-6 mb-4">
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                    Current Price
                  </label>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatPrice(item.price)}
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                    Target Price
                  </label>
                  {editingItem === item.id ? (
                    <input
                      type="number"
                      value={item.targetPrice || ''}
                      onChange={(e) => updateItem(item.id, { targetPrice: e.target.value ? Number(e.target.value) : undefined })}
                      placeholder="Enter target price"
                      className="text-lg font-semibold border border-gray-300 rounded px-3 py-1 w-full"
                    />
                  ) : (
                    <div className="text-lg font-semibold text-gray-900">
                      {formatPrice(item.targetPrice)}
                    </div>
                  )}
                </div>
              </div>

              {/* Status, Rep, and Notes */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                {/* Status */}
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                    Status
                  </label>
                  {editingItem === item.id ? (
                    <select
                      value={item.sourcingStatus}
                      onChange={(e) => updateItem(item.id, { sourcingStatus: e.target.value as any })}
                      className="w-full text-sm border border-gray-300 rounded px-3 py-2"
                    >
                      {SOURCING_STATUS_OPTIONS.map(status => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(item.sourcingStatus)}`}>
                      {SOURCING_STATUS_OPTIONS.find(s => s.value === item.sourcingStatus)?.label}
                    </span>
                  )}
                </div>

                {/* Assigned Rep */}
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                    Assigned Rep
                  </label>
                  {editingItem === item.id ? (
                    <select
                      value={item.assignedRep || ''}
                      onChange={(e) => updateItem(item.id, { assignedRep: e.target.value || undefined })}
                      className="w-full text-sm border border-gray-300 rounded px-3 py-2"
                    >
                      <option value="">Select Rep</option>
                      {REPS.map(rep => (
                        <option key={rep} value={rep}>{rep}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="text-sm text-gray-900">
                      {item.assignedRep || 'Unassigned'}
                    </div>
                  )}
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                    Notes
                  </label>
                  {editingItem === item.id ? (
                    <textarea
                      value={item.notes || ''}
                      onChange={(e) => updateItem(item.id, { notes: e.target.value })}
                      placeholder="Add notes..."
                      className="w-full text-sm border border-gray-300 rounded px-3 py-2 h-20 resize-none"
                    />
                  ) : (
                    <div className="text-sm text-gray-600">
                      {item.notes || 'No notes'}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Sources Section - Nested Rows */}
            {(item.sources && item.sources.length > 0) || item.searchStatus === 'searching' || item.searchStatus === 'error' ? (
              <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-gray-700">Sources</h4>
                  {item.searchStatus === 'searching' && (
                    <div className="flex items-center text-sm text-blue-600">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                      Searching...
                    </div>
                  )}
                  {item.searchStatus === 'error' && (
                    <div className="text-sm text-red-600">Search failed</div>
                  )}
                </div>
                
                {item.sources && item.sources.length > 0 && (
                  <div className="space-y-2">
                    {item.sources.map((source, index) => (
                      <div key={index} className="flex items-center justify-between py-2 px-3 bg-white rounded border border-gray-200">
                        <div className="flex items-center space-x-3">
                          <div className="text-sm font-medium text-gray-900">
                            {source.source}
                          </div>
                          {source.url && (
                            <a
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-600 hover:text-blue-700"
                            >
                              View →
                            </a>
                          )}
                        </div>
                        <div className="text-sm font-semibold text-gray-900">
                          {formatPrice(source.price)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : null}
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