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

export default function LaserMatchTab() {
  const [items, setItems] = useState<LaserMatchItem[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [editingItem, setEditingItem] = useState<string | null>(null)

  // Fetch LaserMatch items on component mount
  useEffect(() => {
    fetchLaserMatchItems()
  }, [])

  const fetchLaserMatchItems = async () => {
    setIsLoading(true)
    try {
      const { apiService } = await import('../services/api')
      const results = await apiService.searchEquipment({ sources: ['LaserMatch.io'] })
      
      if (!results || results.length === 0) {
        console.log('No LaserMatch items found in database. Run the spider first.')
        setItems([])
        return
      }
      
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
          <p className="text-gray-600">Managing {items.length} items from LaserMatch.io</p>
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

      {/* Items Table */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Equipment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assigned Rep
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Target Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sources
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  {/* Equipment Info */}
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      <div className="text-sm font-medium text-gray-900 line-clamp-2">
                        {item.title}
                      </div>
                      <div className="text-sm text-gray-500">
                        {item.brand} {item.model}
                      </div>
                      <div className="text-xs text-gray-400">
                        {item.condition} • {item.location}
                      </div>
                    </div>
                  </td>

                  {/* Current Price */}
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">
                      {formatPrice(item.price)}
                    </div>
                  </td>

                  {/* Assigned Rep */}
                  <td className="px-6 py-4">
                    {editingItem === item.id ? (
                      <select
                        value={item.assignedRep || ''}
                        onChange={(e) => updateItem(item.id, { assignedRep: e.target.value || undefined })}
                        className="text-sm border border-gray-300 rounded px-2 py-1"
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
                  </td>

                  {/* Target Price */}
                  <td className="px-6 py-4">
                    {editingItem === item.id ? (
                      <input
                        type="number"
                        value={item.targetPrice || ''}
                        onChange={(e) => updateItem(item.id, { targetPrice: e.target.value ? Number(e.target.value) : undefined })}
                        placeholder="Target price"
                        className="text-sm border border-gray-300 rounded px-2 py-1 w-24"
                      />
                    ) : (
                      <div className="text-sm text-gray-900">
                        {formatPrice(item.targetPrice)}
                      </div>
                    )}
                  </td>

                  {/* Sourcing Status */}
                  <td className="px-6 py-4">
                    {editingItem === item.id ? (
                      <select
                        value={item.sourcingStatus}
                        onChange={(e) => updateItem(item.id, { sourcingStatus: e.target.value as any })}
                        className="text-sm border border-gray-300 rounded px-2 py-1"
                      >
                        {SOURCING_STATUS_OPTIONS.map(status => (
                          <option key={status.value} value={status.value}>
                            {status.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.sourcingStatus)}`}>
                        {SOURCING_STATUS_OPTIONS.find(s => s.value === item.sourcingStatus)?.label}
                      </span>
                    )}
                  </td>

                  {/* Sources */}
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      {item.searchStatus === 'searching' && (
                        <div className="flex items-center text-xs text-blue-600">
                          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600 mr-1"></div>
                          Searching...
                        </div>
                      )}
                      {item.sources && item.sources.length > 0 && (
                        <div className="text-xs text-gray-600">
                          {item.sources.length} sources found
                        </div>
                      )}
                      {item.searchStatus === 'error' && (
                        <div className="text-xs text-red-600">Search failed</div>
                      )}
                    </div>
                  </td>

                  {/* Notes */}
                  <td className="px-6 py-4">
                    {editingItem === item.id ? (
                      <textarea
                        value={item.notes || ''}
                        onChange={(e) => updateItem(item.id, { notes: e.target.value })}
                        placeholder="Add notes..."
                        className="text-sm border border-gray-300 rounded px-2 py-1 w-32 h-16 resize-none"
                      />
                    ) : (
                      <div className="text-sm text-gray-600 max-w-32 truncate">
                        {item.notes || 'No notes'}
                      </div>
                    )}
                  </td>

                  {/* Actions */}
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      {editingItem === item.id ? (
                        <>
                          <button
                            onClick={() => setEditingItem(null)}
                            className="text-green-600 hover:text-green-700"
                          >
                            <CheckIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => setEditingItem(null)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <XMarkIcon className="h-4 w-4" />
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => findSources(item)}
                            disabled={item.searchStatus === 'searching'}
                            className="text-blue-600 hover:text-blue-700 disabled:text-gray-400"
                            title="Find Sources"
                          >
                            <MagnifyingGlassIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => setEditingItem(item.id)}
                            className="text-gray-600 hover:text-gray-700"
                            title="Edit"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {items.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No items found. Click "Refresh Items" to load LaserMatch items.</p>
        </div>
      )}
    </div>
  )
}