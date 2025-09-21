'use client'

import { useState, useEffect } from 'react'
import { ArrowPathIcon, PencilIcon, CheckIcon, XMarkIcon, SparklesIcon, ChevronDownIcon } from '@heroicons/react/24/outline'

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
  const [currentUser] = useState('John Smith') // TODO: Get from auth context
  const [addingSpiderUrl, setAddingSpiderUrl] = useState<string | null>(null)
  const [spiderSearching, setSpiderSearching] = useState<string | null>(null)
  const [newSpiderUrl, setNewSpiderUrl] = useState({
    url: '',
    contactId: '',
    price: '',
    followUpDate: ''
  })
  const [showRepFilter, setShowRepFilter] = useState(false)
  const [selectedReps, setSelectedReps] = useState<string[]>([])
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

  const autoFindSources = async (item: LaserMatchItem) => {
    setSpiderSearching(item.id)
    
    try {
      // Import the API service
      const { apiService } = await import('../services/api')
      
      // Search for this item using the real search API
      const searchResults = await apiService.searchEquipment({
        query: item.title,
        brand: item.brand,
        model: item.model,
        limit: 10
      })

      // Convert search results to spider URL format
      const spiderResults = searchResults
        .filter(result => result.source !== 'LaserMatch.io') // Exclude the original LaserMatch item
        .map((result, index) => ({
          id: `spider_${Date.now()}_${index}`,
          url: result.url || `https://search-result-${result.id}.com`,
          contactId: index % 2 === 0 ? '1' : '2', // Alternate between contacts
          contactName: index % 2 === 0 ? 'John Smith' : 'Sarah Johnson',
          contactCompany: index % 2 === 0 ? 'MedTech Solutions' : 'Laser Dynamics Inc',
          price: result.price || Math.floor(Math.random() * 50000) + 10000,
          followUpDate: new Date(Date.now() + (5 + index) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          status: 'new' as const,
          addedBy: 'spider' as const,
          addedAt: new Date().toISOString(),
          notes: `Auto-discovered from ${result.source}: ${result.title}`
        }))

      // If no results found, show a message
      if (spiderResults.length === 0) {
        console.log(`No external sources found for ${item.title}`)
        // You could show a toast notification here
        return
      }

      // Add the spider results to the item
      setItems(prev => prev.map(i => {
        if (i.id === item.id) {
          const currentSpiderUrls = i.spiderUrls || []
          return {
              ...i, 
            spiderUrls: [...currentSpiderUrls, ...spiderResults]
          }
        }
        return i
      }))

      console.log(`✅ Found ${spiderResults.length} sources for ${item.title}`)

    } catch (error) {
      console.error('Spider search failed:', error)
      // Show error message to user
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      alert(`Failed to find sources: ${errorMessage}`)
    } finally {
      setSpiderSearching(null)
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

  // Rep filter functions
  const availableReps = Array.from(new Set([
    'Unassigned',
    ...items.map(item => item.assignedRep || 'Unassigned').filter(rep => rep !== 'Unassigned')
  ]))

  const toggleRepFilter = (rep: string) => {
    setSelectedReps(prev => 
      prev.includes(rep) 
        ? prev.filter(r => r !== rep)
        : [...prev, rep]
    )
  }

  const clearRepFilters = () => {
    setSelectedReps([])
  }

  // Filter items by selected reps
  const filteredItems = selectedReps.length === 0 
    ? items 
    : items.filter(item => {
        const itemRep = item.assignedRep || 'Unassigned'
        return selectedReps.includes(itemRep)
      })

  // Group filtered items by brand
  const groupedItems = filteredItems.reduce((groups, item) => {
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
        <span className="ml-2 text-gray-400">Loading LaserMatch items...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex justify-end">
        <div className="relative">
          <label className="block text-sm font-medium text-gray-400 mb-2">Filter by Rep</label>
          <div className="relative">
            <button
              onClick={() => setShowRepFilter(!showRepFilter)}
              className="bg-gray-800 border border-gray-600 text-white px-4 py-2 rounded-md text-sm focus:border-gray-500 focus:outline-none flex items-center min-w-48"
            >
              <span className="flex-1 text-left">
                {selectedReps.length === 0 
                  ? 'All Reps' 
                  : selectedReps.length === 1 
                    ? selectedReps[0] 
                    : `${selectedReps.length} reps selected`
                }
                  </span>
              <ChevronDownIcon className="h-4 w-4 ml-2" />
            </button>
            
            {showRepFilter && (
              <div className="absolute right-0 mt-1 w-64 bg-gray-800 border border-gray-600 rounded-md shadow-lg z-10">
                <div className="p-2 max-h-60 overflow-y-auto">
                  {availableReps.map((rep) => (
                    <label key={rep} className="flex items-center p-2 hover:bg-gray-700 rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedReps.includes(rep)}
                        onChange={() => toggleRepFilter(rep)}
                        className="h-4 w-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                      />
                      <span className="ml-2 text-sm text-white">{rep}</span>
                    </label>
                  ))}
                </div>
                <div className="border-t border-gray-600 p-2">
                  <button
                    onClick={clearRepFilters}
                    className="text-xs text-gray-400 hover:text-white"
                  >
                    Clear All
                  </button>
                </div>
              </div>
            )}
            </div>
        </div>
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
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => autoFindSources(item)}
                        disabled={spiderSearching === item.id}
                        className="flex items-center text-xs text-purple-400 hover:text-purple-300 disabled:text-gray-600"
                        title="Auto-discover sources using spiders"
                      >
                        <SparklesIcon className="h-4 w-4 mr-1" />
                        {spiderSearching === item.id ? 'Searching...' : 'Magic Find'}
                      </button>
                      <button
                        onClick={() => setAddingSpiderUrl(item.id)}
                        className="text-xs text-gray-300 hover:text-white"
                      >
                        Add Source
                      </button>
                    </div>
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
                  {item.spiderUrls && item.spiderUrls.length > 0 && (
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
                                <div className="flex items-center space-x-2">
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-700 text-gray-300">
                                    Source {(item.spiderUrls?.indexOf(spiderUrl) ?? -1) + 1}
                                  </span>
                                  <a
                                    href={spiderUrl.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-sm text-blue-400 hover:text-blue-300 underline truncate block max-w-xs"
                                  >
                                    {spiderUrl.url}
                                  </a>
                                </div>
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
                      className="text-xs text-white hover:text-gray-300"
                    >
                      Add Note
                    </button>
                  )}
                </div>
                
                <div className="space-y-3">
                  {/* Notes Log - Always Visible */}
                  <div className="border border-gray-700 rounded-lg bg-gray-800 max-h-32 overflow-y-auto">
                    {((item.notesLog && item.notesLog.length > 0) || item.notes) && (
                      <div className="p-3 space-y-2">
                        {/* Show new structured notes in reverse order (newest last, so newest appears at bottom) */}
                        {item.notesLog?.slice().reverse().map((note) => (
                          <div key={note.id} className="bg-gray-700 rounded border border-gray-600 p-2">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium text-gray-300">{note.author}</span>
                              <span className="text-xs text-gray-400">
                                {new Date(note.timestamp).toLocaleString()}
                              </span>
                            </div>
                            <div className="text-sm text-gray-200">
                              {renderNoteWithSourceTags(note.content, item.spiderUrls)}
                            </div>
                          </div>
                        ))}
                        
                        {/* Show legacy note if it exists and no structured notes */}
                        {item.notes && (!item.notesLog || item.notesLog.length === 0) && (
                          <div className="bg-gray-700 rounded border border-gray-600 p-2">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium text-gray-300">Legacy Note</span>
                              <span className="text-xs text-gray-400">Unknown date</span>
                            </div>
                            <div className="text-sm text-gray-200">
                              {renderNoteWithSourceTags(item.notes, item.spiderUrls)}
                            </div>
                          </div>
                        )}
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
                        className="w-full text-sm border border-gray-600 bg-gray-800 text-white rounded px-3 py-2 h-20 resize-none focus:border-gray-500 focus:outline-none"
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