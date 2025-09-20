'use client'

import { useState, useEffect } from 'react'
import { ArrowPathIcon, MagnifyingGlassIcon, PencilIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface Note {
  id: string
  content: string
  author: string
  timestamp: string
}

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
    contactName?: string
    contactEmail?: string
    contactPhone?: string
    addedBy?: 'spider' | 'manual'
    addedAt?: string
  }[]
  spiderUrls?: {
    id: string
    url: string
    contactId?: string
    contactName?: string
    contactCompany?: string
    price?: number
    followUpDate?: string
    status: 'new' | 'contacted' | 'quoted' | 'declined' | 'purchased'
    addedBy: 'spider' | 'manual'
    addedAt: string
    notes?: string
  }[]
  searchStatus?: 'idle' | 'searching' | 'completed' | 'error'
  // Procurement fields
  assignedRep?: string
  targetPrice?: number
  sourcingStatus: 'not_started' | 'in_progress' | 'quoted' | 'negotiating' | 'purchased' | 'declined'
  notes?: string // Legacy field for backward compatibility
  notesLog?: Note[] // New structured notes
}

const SOURCING_STATUS_OPTIONS = [
  { value: 'not_started', label: 'Not Started', color: 'bg-gray-100 text-gray-800' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-blue-100 text-blue-800' },
  { value: 'quoted', label: 'Quoted', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'negotiating', label: 'Negotiating', color: 'bg-orange-100 text-orange-800' },
  { value: 'purchased', label: 'Purchased', color: 'bg-green-100 text-green-800' },
  { value: 'declined', label: 'Declined', color: 'bg-red-100 text-red-800' }
]

// Users will be loaded dynamically from configuration
const DEFAULT_REPS = ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Chen', 'Tom Wilson']

// Helper function to extract brand and model from title
const cleanTitle = (title: string): string => {
  // If title contains a colon, take brand and model (everything before newline)
  if (title.includes(':')) {
    const firstLine = title.split('\n')[0].trim()
    // Return the brand: model part
    return firstLine
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
  const [newNoteContent, setNewNoteContent] = useState('')
  const [addingSource, setAddingSource] = useState<string | null>(null)
  const [newSource, setNewSource] = useState({
    source: '',
    url: '',
    price: '',
    contactName: '',
    contactEmail: '',
    contactPhone: ''
  })
  const [currentUser] = useState('John Smith') // TODO: Get from auth context
  const [addingSpiderUrl, setAddingSpiderUrl] = useState<string | null>(null)
  const [newSpiderUrl, setNewSpiderUrl] = useState({
    url: '',
    contactId: '',
    price: '',
    followUpDate: ''
  })
  // Mock contacts data - in real app this would come from contacts context/API
  const [contacts] = useState([
    { id: '1', name: 'John Smith', company: 'MedTech Solutions', email: 'john.smith@medtech.com' },
    { id: '2', name: 'Sarah Johnson', company: 'Laser Dynamics Inc', email: 'sarah@laserdynamics.com' },
    { id: '3', name: 'Mike Wilson', company: 'Equipment Direct', email: 'mike@equipmentdirect.com' }
  ])
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

  const addNote = (itemId: string, content: string) => {
    if (!content.trim()) return

    const newNote: Note = {
      id: Date.now().toString(),
      content: content.trim(),
      author: currentUser,
      timestamp: new Date().toISOString()
    }

    setItems(prev => prev.map(item => {
      if (item.id === itemId) {
        const currentNotes = item.notesLog || []
        return {
          ...item,
          notesLog: [...currentNotes, newNote] // Add new note at the end (newest last)
        }
      }
      return item
    }))

    setNewNoteContent('')
    setEditingItem(null)
  }

  const addSource = (itemId: string) => {
    if (!newSource.source.trim() || !newSource.url.trim()) return

    const sourceToAdd = {
      source: newSource.source.trim(),
      url: newSource.url.trim(),
      price: newSource.price ? Number(newSource.price) : undefined,
      found: true,
      contactName: newSource.contactName.trim() || undefined,
      contactEmail: newSource.contactEmail.trim() || undefined,
      contactPhone: newSource.contactPhone.trim() || undefined,
      addedBy: 'manual' as const,
      addedAt: new Date().toISOString()
    }

    setItems(prev => prev.map(item => {
      if (item.id === itemId) {
        const currentSources = item.sources || []
        return {
          ...item,
          sources: [...currentSources, sourceToAdd]
        }
      }
      return item
    }))

    // Reset form
    setNewSource({
      source: '',
      url: '',
      price: '',
      contactName: '',
      contactEmail: '',
      contactPhone: ''
    })
    setAddingSource(null)
  }

  const addSpiderUrl = (itemId: string) => {
    if (!newSpiderUrl.url.trim() || !newSpiderUrl.contactId.trim()) return

    const selectedContact = contacts.find(c => c.id === newSpiderUrl.contactId)
    
    const spiderUrl = {
      id: Date.now().toString(),
      url: newSpiderUrl.url.trim(),
      contactId: newSpiderUrl.contactId,
      contactName: selectedContact?.name,
      contactCompany: selectedContact?.company,
      price: newSpiderUrl.price ? Number(newSpiderUrl.price) : undefined,
      followUpDate: newSpiderUrl.followUpDate || undefined,
      status: 'new' as const,
      addedBy: 'manual' as const,
      addedAt: new Date().toISOString()
    }

    setItems(prev => prev.map(item => {
      if (item.id === itemId) {
        const currentSpiderUrls = item.spiderUrls || []
        return {
          ...item,
          spiderUrls: [...currentSpiderUrls, spiderUrl]
        }
      }
      return item
    }))

    // Reset form
    setNewSpiderUrl({
      url: '',
      contactId: '',
      price: '',
      followUpDate: ''
    })
    setAddingSpiderUrl(null)
  }

  const updateSpiderUrl = (itemId: string, spiderUrlId: string, updates: any) => {
    setItems(prev => prev.map(item => {
      if (item.id === itemId) {
        const updatedSpiderUrls = item.spiderUrls?.map(spiderUrl =>
          spiderUrl.id === spiderUrlId ? { ...spiderUrl, ...updates } : spiderUrl
        )
        return { ...item, spiderUrls: updatedSpiderUrls }
      }
      return item
    }))
  }

  const deleteSpiderUrl = (itemId: string, spiderUrlId: string) => {
    if (confirm('Are you sure you want to delete this source?')) {
      setItems(prev => prev.map(item => {
        if (item.id === itemId) {
          const updatedSpiderUrls = item.spiderUrls?.filter(spiderUrl => spiderUrl.id !== spiderUrlId)
          return { ...item, spiderUrls: updatedSpiderUrls }
        }
        return item
      }))
    }
  }

  const getSpiderUrlStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'bg-blue-100 text-blue-800'
      case 'contacted': return 'bg-yellow-100 text-yellow-800'
      case 'quoted': return 'bg-purple-100 text-purple-800'
      case 'declined': return 'bg-red-100 text-red-800'
      case 'purchased': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const renderNoteWithSourceTags = (noteContent: string, spiderUrls?: any[]) => {
    if (!spiderUrls || spiderUrls.length === 0) {
      return noteContent
    }

    // Replace @source-X tags with highlighted spans
    let processedContent = noteContent
    spiderUrls.forEach((spiderUrl, index) => {
      const tag = `@source-${index + 1}`
      const regex = new RegExp(tag, 'gi')
      processedContent = processedContent.replace(
        regex,
        `<span class="inline-flex items-center px-2 py-0.5 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">${tag}: ${spiderUrl.contactName || 'Unknown'}</span>`
      )
    })

    return <div dangerouslySetInnerHTML={{ __html: processedContent }} />
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

  // Group items by brand
  const groupedItems = items.reduce((groups, item) => {
    const brand = item.brand || 'Unknown'
    if (!groups[brand]) {
      groups[brand] = []
    }
    groups[brand].push(item)
    return groups
  }, {} as Record<string, typeof items>)

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
          <h2 className="text-2xl font-bold text-white">LaserMatch Procurement</h2>
          <p className="text-gray-400">
            {stats ? (
              <>
                Managing {stats.total_items} items from LaserMatch.io
                {stats.latest_update && (
                  <span className="text-sm text-gray-400 ml-2">
                    • Last updated: {new Date(stats.latest_update).toLocaleString()}
                  </span>
                )}
              </>
            ) : (
              `Managing ${items.length} items from LaserMatch.io`
            )}
          </p>
          {stats && (
            <div className="flex space-x-4 text-sm text-gray-400 mt-1">
              <span>🔥 Hot List: {stats.hot_list_items} items</span>
              <span>📈 In Demand: {stats.in_demand_items} items</span>
            </div>
          )}
        </div>
        <button
          onClick={refreshLaserMatchItems}
          disabled={isRefreshing}
          className="bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 text-white px-4 py-2 rounded-md font-medium flex items-center transition-colors"
        >
          <ArrowPathIcon className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? 'Refreshing...' : 'Refresh Items'}
        </button>
      </div>

      {/* Grouped Items by Brand */}
      <div className="space-y-8">
        {Object.entries(groupedItems).map(([brand, brandItems]) => (
          <div key={brand} className="space-y-4">
            {/* Brand Title */}
            <div className="text-center">
              <h3 className="text-2xl font-bold text-orange-400 mb-2">{brand}</h3>
              <div className="w-16 h-0.5 bg-orange-400 mx-auto"></div>
            </div>
            
            {/* Brand Items */}
            <div className="space-y-3">
              {brandItems.map((item) => (
          <div key={item.id} className="bg-gray-900 shadow-sm rounded-lg border border-gray-800 overflow-hidden">
            {/* Main Card Content */}
            <div className="p-4">
              <div className="flex justify-between items-start mb-4">
                  {/* Equipment Info */}
                <div className="flex-1 min-w-0 mr-6">
                  <h3 className="text-lg font-medium text-white mb-3 line-clamp-2">
                    {cleanTitle(item.title)}
                  </h3>
                  <div className="text-sm text-gray-300">
                    {item.description}
                      </div>
                      </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 flex-shrink-0">
                  {editingItem === item.id ? (
                    <>
                      <button
                        onClick={() => setEditingItem(null)}
                        className="text-gray-300 hover:text-white p-2"
                        title="Save"
                      >
                        <CheckIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => setEditingItem(null)}
                        className="text-gray-400 hover:text-gray-300 p-2"
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
                        className="text-gray-300 hover:text-white disabled:text-gray-600 p-2"
                        title="Find Sources"
                      >
                        <MagnifyingGlassIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => setEditingItem(item.id)}
                        className="text-gray-400 hover:text-gray-300 p-2"
                        title="Edit"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </button>
                    </>
                  )}
                      </div>
                    </div>

              {/* All Key Fields in One Row */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">
                    Current Price
                  </label>
                  {editingItem === item.id ? (
                    <input
                      type="number"
                      value={item.price || ''}
                      onChange={(e) => updateItem(item.id, { price: e.target.value ? Number(e.target.value) : undefined })}
                      placeholder="Enter current price"
                      className="text-sm font-semibold border border-gray-600 bg-gray-800 text-white rounded px-2 py-1 w-full focus:border-gray-500 focus:outline-none"
                    />
                  ) : (
                    <div className="text-sm font-semibold text-white">
                      {formatPrice(item.price)}
                    </div>
                  )}
                      </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">
                    Target Price
                  </label>
                    {editingItem === item.id ? (
                      <input
                        type="number"
                        value={item.targetPrice || ''}
                        onChange={(e) => updateItem(item.id, { targetPrice: e.target.value ? Number(e.target.value) : undefined })}
                      placeholder="Enter target price"
                      className="text-sm font-semibold border border-gray-600 bg-gray-800 text-white rounded px-2 py-1 w-full focus:border-gray-500 focus:outline-none"
                      />
                    ) : (
                    <div className="text-sm font-semibold text-white">
                        {formatPrice(item.targetPrice)}
                      </div>
                    )}
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">
                    Status
                  </label>
                    {editingItem === item.id ? (
                      <select
                        value={item.sourcingStatus}
                        onChange={(e) => updateItem(item.id, { sourcingStatus: e.target.value as any })}
                      className="w-full text-xs border border-gray-600 bg-gray-800 text-white rounded px-2 py-1 focus:border-gray-500 focus:outline-none"
                      >
                        {SOURCING_STATUS_OPTIONS.map(status => (
                          <option key={status.value} value={status.value}>
                            {status.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.sourcingStatus)}`}>
                        {SOURCING_STATUS_OPTIONS.find(s => s.value === item.sourcingStatus)?.label}
                      </span>
                    )}
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">
                    Assigned Rep
                  </label>
                  {editingItem === item.id ? (
                    <select
                      value={item.assignedRep || ''}
                      onChange={(e) => updateItem(item.id, { assignedRep: e.target.value || undefined })}
                      className="w-full text-xs border border-gray-600 bg-gray-800 text-white rounded px-2 py-1 focus:border-gray-500 focus:outline-none"
                    >
                      <option value="">Select Rep</option>
                      {DEFAULT_REPS.map(rep => (
                        <option key={rep} value={rep}>{rep}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="text-xs text-white">
                      {item.assignedRep || 'Unassigned'}
                        </div>
                      )}
                </div>
              </div>

              {/* Spider URLs Section - Full Width */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Spider Crawled URLs & Sources
                  </label>
                  {addingSpiderUrl !== item.id && (
                    <button
                      onClick={() => setAddingSpiderUrl(item.id)}
                      className="text-xs text-gray-300 hover:text-white"
                    >
                      Add Source
                    </button>
                  )}
                </div>

                {/* Add Spider URL Form */}
                {addingSpiderUrl === item.id && (
                  <div className="mb-4 p-3 bg-gray-800 rounded border border-gray-700">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-3">
                      <input
                        type="url"
                        placeholder="URL *"
                        value={newSpiderUrl.url}
                        onChange={(e) => setNewSpiderUrl(prev => ({ ...prev, url: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                      <select
                        value={newSpiderUrl.contactId}
                        onChange={(e) => setNewSpiderUrl(prev => ({ ...prev, contactId: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      >
                        <option value="">Select Contact *</option>
                        {contacts.map(contact => (
                          <option key={contact.id} value={contact.id}>
                            {contact.name} - {contact.company}
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        placeholder="Price"
                        value={newSpiderUrl.price}
                        onChange={(e) => setNewSpiderUrl(prev => ({ ...prev, price: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                      <input
                        type="date"
                        placeholder="Follow-up date"
                        value={newSpiderUrl.followUpDate}
                        onChange={(e) => setNewSpiderUrl(prev => ({ ...prev, followUpDate: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                    </div>
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => {
                          setAddingSpiderUrl(null)
                          setNewSpiderUrl({
                            url: '',
                            contactId: '',
                            price: '',
                            followUpDate: ''
                          })
                        }}
                        className="px-3 py-1 text-xs text-gray-400 hover:text-gray-300"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => addSpiderUrl(item.id)}
                        disabled={!newSpiderUrl.url.trim() || !newSpiderUrl.contactId.trim()}
                        className="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500 disabled:bg-gray-700 disabled:cursor-not-allowed"
                      >
                        Add Source
                      </button>
                    </div>
                        </div>
                      )}

                {/* Spider URLs List */}
                <div className="border border-gray-700 rounded-lg bg-gray-800">
                  {item.spiderUrls && item.spiderUrls.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-700">
                        <thead className="bg-gray-900">
                          <tr>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                              URL
                            </th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                              Contact
                            </th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                              Price
                            </th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                              Follow Up
                            </th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                              Status
                            </th>
                            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Actions
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-gray-800 divide-y divide-gray-700">
                          {item.spiderUrls.map((spiderUrl) => (
                            <tr key={spiderUrl.id} className="hover:bg-gray-700">
                              <td className="px-3 py-2 whitespace-nowrap">
                                <a
                                  href={spiderUrl.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-sm text-gray-300 hover:text-white truncate block max-w-xs"
                                >
                                  {spiderUrl.url}
                                </a>
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap">
                                <div>
                                  <div className="text-sm font-medium text-white">{spiderUrl.contactName || 'No contact'}</div>
                                  {spiderUrl.contactCompany && (
                                    <div className="text-xs text-gray-400">{spiderUrl.contactCompany}</div>
                      )}
                    </div>
                  </td>
                              <td className="px-3 py-2 whitespace-nowrap text-sm text-white">
                                {formatPrice(spiderUrl.price)}
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap text-sm text-white">
                                {spiderUrl.followUpDate ? new Date(spiderUrl.followUpDate).toLocaleDateString() : 'Not set'}
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap">
                                <select
                                  value={spiderUrl.status}
                                  onChange={(e) => updateSpiderUrl(item.id, spiderUrl.id, { status: e.target.value })}
                                  className={`text-xs px-2 py-1 rounded-full border-0 font-medium ${getSpiderUrlStatusColor(spiderUrl.status)}`}
                                >
                                  <option value="new">New</option>
                                  <option value="contacted">Contacted</option>
                                  <option value="quoted">Quoted</option>
                                  <option value="declined">Declined</option>
                                  <option value="purchased">Purchased</option>
                                </select>
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap text-right text-sm font-medium">
                                <button
                                  onClick={() => deleteSpiderUrl(item.id, spiderUrl.id)}
                                  className="text-red-600 hover:text-red-700 text-xs"
                                >
                                  Delete
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="p-4 text-center text-sm text-gray-500">
                      No sources found yet. Spider crawls and manual entries will appear here.
                    </div>
                  )}
                </div>
              </div>

              {/* Notes Log - Full Width */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Notes Log
                  </label>
                  {editingItem !== item.id && (
                    <button
                      onClick={() => setEditingItem(item.id)}
                      className="text-xs text-blue-600 hover:text-blue-700"
                    >
                      Add Note
                    </button>
                  )}
                </div>
                
                <div className="space-y-3">
                  {/* Notes Log - Always Visible */}
                  <div className="border border-gray-200 rounded-lg bg-gray-50 max-h-32 overflow-y-auto">
                    {(item.notesLog && item.notesLog.length > 0) || item.notes ? (
                      <div className="p-3 space-y-2">
                        {/* Show new structured notes in reverse order (newest last, so newest appears at bottom) */}
                        {item.notesLog?.slice().reverse().map((note) => (
                          <div key={note.id} className="bg-white rounded border border-gray-100 p-2">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium text-gray-700">{note.author}</span>
                              <span className="text-xs text-gray-500">
                                {new Date(note.timestamp).toLocaleString()}
                              </span>
                            </div>
                            <div className="text-sm text-gray-800">
                              {renderNoteWithSourceTags(note.content, item.spiderUrls)}
                            </div>
                          </div>
                        ))}
                        
                        {/* Show legacy note if it exists and no structured notes */}
                        {item.notes && (!item.notesLog || item.notesLog.length === 0) && (
                          <div className="bg-white rounded border border-gray-100 p-2">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium text-gray-700">Legacy Note</span>
                              <span className="text-xs text-gray-500">Unknown date</span>
                            </div>
                            <div className="text-sm text-gray-800">
                              {renderNoteWithSourceTags(item.notes, item.spiderUrls)}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="p-3 text-sm text-gray-500 text-center">
                        No notes yet. Click "Add Note" to get started.
                      </div>
                    )}
                  </div>

                  {/* Add Note Form - Show when editing */}
                  {editingItem === item.id && (
                    <div className="space-y-2">
                      <textarea
                        value={newNoteContent}
                        onChange={(e) => setNewNoteContent(e.target.value)}
                        placeholder="Add a new note... (Use @source-1, @source-2, etc. to tag specific sources)"
                        className="w-full text-sm border border-gray-300 rounded px-3 py-2 h-20 resize-none"
                      />
                      {item.spiderUrls && item.spiderUrls.length > 0 && (
                        <div className="mt-2 text-xs text-gray-500">
                          <div className="font-medium mb-1">Available sources to tag:</div>
                          <div className="flex flex-wrap gap-2">
                            {item.spiderUrls.map((spiderUrl, index) => (
                              <span
                                key={spiderUrl.id}
                                className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded cursor-pointer hover:bg-gray-200"
                                onClick={() => {
                                  const tag = `@source-${index + 1}`
                                  setNewNoteContent(prev => prev + (prev ? ' ' : '') + tag)
                                }}
                              >
                                @source-{index + 1}: {spiderUrl.contactName || 'Unknown'}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => {
                            setEditingItem(null)
                            setNewNoteContent('')
                          }}
                          className="px-3 py-1 text-xs text-gray-400 hover:text-gray-300"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => addNote(item.id, newNoteContent)}
                          disabled={!newNoteContent.trim()}
                          className="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500 disabled:bg-gray-700 disabled:cursor-not-allowed"
                        >
                          Add Note
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Sources Section - Nested Rows */}
            {(item.sources && item.sources.length > 0) || item.searchStatus === 'searching' || item.searchStatus === 'error' || addingSource === item.id ? (
              <div className="border-t border-gray-200 bg-gray-50 px-4 py-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-gray-700">Sources</h4>
                  <div className="flex items-center space-x-2">
                    {item.searchStatus === 'searching' && (
                      <div className="flex items-center text-sm text-blue-600">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                        Searching...
                      </div>
                    )}
                    {item.searchStatus === 'error' && (
                      <div className="text-sm text-red-600">Search failed</div>
                    )}
                    {addingSource !== item.id && (
                          <button
                        onClick={() => setAddingSource(item.id)}
                        className="text-xs text-blue-600 hover:text-blue-700"
                          >
                        Add Source
                          </button>
                    )}
                  </div>
                </div>
                
                {/* Add Source Form */}
                {addingSource === item.id && (
                  <div className="mb-4 p-3 bg-white rounded border border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                      <input
                        type="text"
                        placeholder="Source name *"
                        value={newSource.source}
                        onChange={(e) => setNewSource(prev => ({ ...prev, source: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                      <input
                        type="url"
                        placeholder="Website URL *"
                        value={newSource.url}
                        onChange={(e) => setNewSource(prev => ({ ...prev, url: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                      <input
                        type="number"
                        placeholder="Price"
                        value={newSource.price}
                        onChange={(e) => setNewSource(prev => ({ ...prev, price: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                      <input
                        type="text"
                        placeholder="Contact name"
                        value={newSource.contactName}
                        onChange={(e) => setNewSource(prev => ({ ...prev, contactName: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                      <input
                        type="email"
                        placeholder="Contact email"
                        value={newSource.contactEmail}
                        onChange={(e) => setNewSource(prev => ({ ...prev, contactEmail: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                      <input
                        type="tel"
                        placeholder="Contact phone"
                        value={newSource.contactPhone}
                        onChange={(e) => setNewSource(prev => ({ ...prev, contactPhone: e.target.value }))}
                        className="text-sm border border-gray-600 bg-gray-700 text-white rounded px-3 py-2 focus:border-gray-500 focus:outline-none"
                      />
                    </div>
                    <div className="flex justify-end space-x-2">
                          <button
                        onClick={() => {
                          setAddingSource(null)
                          setNewSource({
                            source: '',
                            url: '',
                            price: '',
                            contactName: '',
                            contactEmail: '',
                            contactPhone: ''
                          })
                        }}
                        className="px-3 py-1 text-xs text-gray-400 hover:text-gray-300"
                      >
                        Cancel
                          </button>
                          <button
                        onClick={() => addSource(item.id)}
                        disabled={!newSource.source.trim() || !newSource.url.trim()}
                        className="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500 disabled:bg-gray-700 disabled:cursor-not-allowed"
                      >
                        Add Source
                          </button>
                    </div>
                  </div>
                )}

                {/* Sources List */}
                {item.sources && item.sources.length > 0 && (
                  <div className="space-y-2">
                    {item.sources.map((source, index) => (
                      <div key={index} className="bg-white rounded border border-gray-200 p-3">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <div className="text-sm font-medium text-gray-900">
                              {source.source}
                            </div>
                            {source.addedBy === 'manual' && (
                              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                Manual
                              </span>
                            )}
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
                        
                        {/* Contact Information */}
                        {(source.contactName || source.contactEmail || source.contactPhone) && (
                          <div className="text-xs text-gray-600 space-y-1">
                            {source.contactName && (
                              <div>Contact: {source.contactName}</div>
                            )}
                            {source.contactEmail && (
                              <div>Email: <a href={`mailto:${source.contactEmail}`} className="text-blue-600 hover:text-blue-700">{source.contactEmail}</a></div>
                            )}
                            {source.contactPhone && (
                              <div>Phone: <a href={`tel:${source.contactPhone}`} className="text-blue-600 hover:text-blue-700">{source.contactPhone}</a></div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : null}
        </div>
              ))}
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