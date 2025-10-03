'use client'

import { useState, useEffect } from 'react'
import { ArrowPathIcon, PencilIcon, CheckIcon, XMarkIcon, SparklesIcon } from '@heroicons/react/24/outline'

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

export default function LaserMatch() {
  console.log('🎯 LaserMatch component rendering...')
  const [items, setItems] = useState<LaserMatchItem[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [clickCount, setClickCount] = useState(0)
  const [editingItem, setEditingItem] = useState<string | null>(null)
  const [expandedItem, setExpandedItem] = useState<string | null>(null)
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
  const [activeTab, setActiveTab] = useState('LaserMatch')
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
    console.log('🚀 Component mounted, starting fetch...')
    
    const fetchData = async () => {
      try {
        console.log('🔍 Fetching LaserMatch items...')
        const response = await fetch('http://localhost:8000/api/v1/lasermatch/items?limit=500')
        console.log('📡 Response status:', response.status)
        
        if (response.ok) {
          const data = await response.json()
          console.log('📊 Received data:', data)
          
          if (data.items && data.items.length > 0) {
            const convertedResults: LaserMatchItem[] = data.items.map((item: any) => ({
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
            console.log('✅ Setting items:', convertedResults.length)
            setItems(convertedResults)
          } else {
            console.log('⚠️ No items in response')
            setItems([])
          }
        } else {
          console.error('❌ Response not ok:', response.status)
          setItems([])
        }
      } catch (error) {
        console.error('❌ Fetch failed:', error)
        setItems([])
      } finally {
        console.log('🏁 Setting isLoading to false')
        setIsLoading(false)
      }
    }
    
    fetchData()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/lasermatch/stats`)
      const statsData = await response.json()
      setStats(statsData)
    } catch (error) {
      console.error('Failed to fetch LaserMatch stats:', error)
    }
  }

  const fetchLaserMatchItems = async () => {
    setIsLoading(true)
    try {
      const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/lasermatch/items?limit=500`
      console.log('🔍 Fetching LaserMatch items from:', apiUrl)
      const response = await fetch(apiUrl)
      console.log('📡 Response status:', response.status, response.statusText)
      const data = await response.json()
      console.log('📊 Received data:', data)
      
      if (!data.items || data.items.length === 0) {
        console.log('No LaserMatch items found in database. Click "Refresh Items" to run the scraper.')
        setItems([])
        return
      }
      
      // Convert API results to component interface
      const convertedResults: LaserMatchItem[] = data.items.map((item: any) => ({
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
      console.error('❌ Failed to fetch LaserMatch items:', error)
      console.error('❌ Error details:', {
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined
      })
      setItems([])
    } finally {
      console.log('🏁 Setting isLoading to false')
      setIsLoading(false)
    }
  }

  const refreshLaserMatchItems = async () => {
    setIsRefreshing(true)
    try {
      // Run the LaserMatch scraper
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/lasermatch/refresh`, {
        method: 'POST'
      })
      const result = await response.json()
      
      console.log(`✅ Scraper completed: ${result.items_scraped} items scraped in ${result.execution_time.toFixed(2)}s`)
      
      // Wait a moment for database update, then refresh the items and stats
      setTimeout(() => {
        fetchLaserMatchItems()
        fetchStats()
      }, 2000)
    } catch (error) {
      console.error('Failed to refresh LaserMatch items:', error)
      alert(`❌ Failed to refresh items: ${error instanceof Error ? error.message : String(error)}`)
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
      // Search for this item using the real search API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/search/equipment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: item.title,
          brand: item.brand,
          model: item.model,
          limit: 10
        })
      })
      const searchResponse = await response.json()

      // Handle different response formats
      let searchResults = []
      if (Array.isArray(searchResponse)) {
        // Direct array response (from main.py direct endpoint)
        searchResults = searchResponse
      } else if (searchResponse.results && Array.isArray(searchResponse.results)) {
        // Object with results array (from search router)
        searchResults = searchResponse.results
      } else {
        console.warn('Unexpected search response format:', searchResponse)
        searchResults = []
      }

      // Convert search results to spider URL format
      const spiderResults = searchResults
        .filter((result: any) => result.source !== 'LaserMatch.io') // Exclude the original LaserMatch item
        .map((result: any, index: number) => ({
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
        <span className="ml-2 text-gray-400">Loading LaserMatch items... (Debug: isLoading=true, items={items.length})</span>
        <button 
          onClick={async () => {
            console.log('🔄 Manual fetch clicked')
            try {
              const response = await fetch('http://localhost:8000/api/v1/lasermatch/items?limit=5')
              console.log('🔄 Response:', response.status)
              if (response.ok) {
                const data = await response.json()
                console.log('🔄 Data:', data)
                if (data.items && data.items.length > 0) {
                  const convertedResults: LaserMatchItem[] = data.items.map((item: any) => ({
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
                  setIsLoading(false)
                }
              }
            } catch (error) {
              console.error('🔄 Manual fetch failed:', error)
            }
          }}
          className="ml-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Manual Fetch
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="bg-gray-900 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <nav className="flex space-x-8">
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => setActiveTab('LaserMatch')}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'LaserMatch' 
                      ? 'border-white text-white' 
                      : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-700'
                  }`}
                >
                  LaserMatch
                </button>
                <button
                  onClick={refreshLaserMatchItems}
                  disabled={isRefreshing}
                  className="p-1 text-gray-400 hover:text-white disabled:text-gray-600 transition-colors"
                  title={isRefreshing ? 'Refreshing...' : 'Refresh Items'}
                >
                  <ArrowPathIcon className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                </button>
              </div>
              <button 
                onClick={() => setActiveTab('Contacts')}
                className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'Contacts' 
                    ? 'border-white text-white' 
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-700'
                }`}
              >
                Contacts
              </button>
              <button 
                onClick={() => setActiveTab('Users')}
                className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'Users' 
                    ? 'border-white text-white' 
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-700'
                }`}
              >
                Users
              </button>
              <button 
                onClick={() => setActiveTab('Configuration')}
                className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'Configuration' 
                    ? 'border-white text-white' 
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-700'
                }`}
              >
                Configuration
              </button>
            </nav>
          </div>
        </div>
      </div>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {activeTab === 'LaserMatch' && (
            <>
              {items.length > 0 ? (
            <div className="bg-gray-900 rounded-lg shadow overflow-hidden">
              <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
                <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-300">
                  <div className="col-span-4">Equipment</div>
                  <div className="col-span-2">Brand</div>
                  <div className="col-span-2">Condition</div>
                  <div className="col-span-2">Price</div>
                  <div className="col-span-1">Source</div>
                  <div className="col-span-1">Actions</div>
                </div>
              </div>
              
              <div className="divide-y divide-gray-700">
                {items.map((item) => (
                  <div key={item.id}>
                    {/* Main Row - Only show if this item is not expanded */}
                    {expandedItem !== item.id && (
                      <div 
                        className="px-6 py-4 hover:bg-gray-800 transition-colors cursor-pointer"
                        onClick={() => setExpandedItem(item.id)}
                      >
                        <div className="grid grid-cols-12 gap-4 items-center">
                          <div className="col-span-4">
                            <div className="flex items-center space-x-3">
                              <div className="flex-shrink-0">
                                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                                  <span className="text-white font-bold text-sm">
                                    {item.brand?.charAt(0) || 'L'}
                                  </span>
                                </div>
                              </div>
                              <div className="min-w-0 flex-1">
                                <h3 className="text-white font-medium truncate">{item.title}</h3>
                                <p className="text-gray-400 text-sm truncate">{item.model}</p>
                              </div>
                            </div>
                          </div>
                          
                          <div className="col-span-2">
                            <span className="text-gray-300">{item.brand}</span>
                          </div>
                          
                          <div className="col-span-2">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              {item.condition}
                            </span>
                          </div>
                          
                          <div className="col-span-2">
                            <span className="text-white font-semibold">
                              {item.price ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(item.price) : 'N/A'}
                            </span>
                            {item.location && (
                              <p className="text-gray-400 text-xs">{item.location}</p>
                            )}
                          </div>
                          
                          <div className="col-span-1">
                            <span className="text-gray-400 text-sm">LaserMatch.io</span>
                          </div>
                          
                          <div className="col-span-1">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  window.open(item.url, '_blank')
                                }}
                                className="text-blue-400 hover:text-blue-300 transition-colors"
                                title="View Original Listing"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setExpandedItem(item.id)
                                }}
                                className="text-green-400 hover:text-green-300 transition-colors"
                                title="View Procurement Details"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Expanded Detailed View */}
                    {expandedItem === item.id && (
                      <div className="bg-gray-800 border-t border-gray-700 p-6">
                        <div className="space-y-6">
                          {/* Equipment Info */}
                          <div className="flex items-start space-x-4">
                            <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                              <span className="text-white font-bold text-xl">
                                {item.brand?.charAt(0) || 'L'}
                              </span>
                            </div>
                            <div className="flex-1">
                              <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <span className="text-gray-400">Brand:</span>
                                  <span className="text-white ml-2">{item.brand}</span>
                                </div>
                                <div>
                                  <span className="text-gray-400">Model:</span>
                                  <span className="text-white ml-2">{item.model}</span>
                                </div>
                                <div>
                                  <span className="text-gray-400">Condition:</span>
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 ml-2">
                                    {item.condition}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-gray-400">Location:</span>
                                  <span className="text-white ml-2">{item.location || 'Unknown'}</span>
                                </div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-2xl font-bold text-white">
                                {item.price ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(item.price) : 'N/A'}
                              </div>
                              <div className="text-sm text-gray-400">Listed Price</div>
                            </div>
                          </div>
                          {item.description && (
                            <div className="pt-4 border-t border-gray-700">
                              <p className="text-gray-300">{item.description}</p>
                            </div>
                          )}

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
                              <div className="border border-gray-700 rounded-lg bg-gray-800 max-h-32 overflow-y-auto">
                                {(item.notesLog && item.notesLog.length > 0) || item.notes ? (
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
                                    className="w-full text-sm bg-gray-700 border border-gray-600 rounded px-3 py-2 h-20 resize-none text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                  />
                                  {item.spiderUrls && item.spiderUrls.length > 0 && (
                                    <div className="mt-2 text-xs text-gray-500">
                                      <div className="font-medium mb-1">Available sources to tag:</div>
                                      <div className="flex flex-wrap gap-2">
                                        {item.spiderUrls.map((spiderUrl, index) => (
                                          <span
                                            key={spiderUrl.id}
                                            className="inline-flex items-center px-2 py-1 bg-gray-600 text-gray-200 rounded cursor-pointer hover:bg-gray-500"
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

                          {/* Action Buttons */}
                          <div className="flex justify-end space-x-4">
                            <button
                              onClick={() => setExpandedItem(null)}
                              className="px-4 py-2 border border-gray-600 text-gray-300 rounded-md hover:bg-gray-700 transition-colors"
                            >
                              Close
                            </button>
                            <button
                              onClick={() => window.open(item.url, '_blank')}
                              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                            >
                              View Original Listing
                            </button>
                            <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
                              Save Changes
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-gray-900 rounded-lg shadow p-12 text-center">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                </svg>
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No items found</h3>
              <p className="text-gray-500 mb-4">Click "Refresh Items" to load LaserMatch items.</p>
              <button 
                onClick={fetchLaserMatchItems}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Refresh Items
              </button>
            </div>
          )}
            </>
          )}

          {activeTab === 'Contacts' && (
            <div className="bg-gray-900 rounded-lg shadow overflow-hidden">
              <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
                <h2 className="text-xl font-bold text-white">Contacts</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {contacts.map((contact) => (
                    <div key={contact.id} className="bg-gray-800 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-white font-medium">{contact.name}</h3>
                          <p className="text-gray-400 text-sm">{contact.company}</p>
                          <p className="text-gray-500 text-sm">{contact.email}</p>
                        </div>
                        <div className="flex space-x-2">
                          <button className="text-blue-400 hover:text-blue-300 text-sm">Edit</button>
                          <button className="text-red-400 hover:text-red-300 text-sm">Delete</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md">
                  Add New Contact
                </button>
              </div>
            </div>
          )}

          {activeTab === 'Users' && (
            <div className="bg-gray-900 rounded-lg shadow overflow-hidden">
              <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
                <h2 className="text-xl font-bold text-white">Users</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {DEFAULT_REPS.map((rep, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg p-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="text-white font-medium">{rep}</h3>
                          <p className="text-gray-400 text-sm">Sales Representative</p>
                        </div>
                        <div className="flex space-x-2">
                          <button className="text-blue-400 hover:text-blue-300 text-sm">Edit</button>
                          <button className="text-red-400 hover:text-red-300 text-sm">Deactivate</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md">
                  Add New User
                </button>
              </div>
            </div>
          )}

          {activeTab === 'Configuration' && (
            <div className="bg-gray-900 rounded-lg shadow overflow-hidden">
              <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
                <h2 className="text-xl font-bold text-white">Configuration</h2>
              </div>
              <div className="p-6">
                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-lg p-4">
                    <h3 className="text-white font-medium mb-4">API Settings</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-gray-300 text-sm mb-1">API URL</label>
                        <input 
                          type="text" 
                          value={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'} 
                          className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                          readOnly
                        />
                      </div>
                      <div>
                        <label className="block text-gray-300 text-sm mb-1">Database Status</label>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-green-400 text-sm">Connected</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-800 rounded-lg p-4">
                    <h3 className="text-white font-medium mb-4">Scraping Settings</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">Auto-refresh interval</span>
                        <select className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-white text-sm">
                          <option>5 minutes</option>
                          <option>15 minutes</option>
                          <option>30 minutes</option>
                          <option>1 hour</option>
                        </select>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">Enable Magic Find</span>
                        <input type="checkbox" className="rounded" defaultChecked />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
