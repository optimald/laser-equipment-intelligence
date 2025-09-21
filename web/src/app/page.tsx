'use client'

import { useState } from 'react'
import { MagnifyingGlassIcon, CogIcon, UserGroupIcon, UsersIcon, ChevronDownIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import LaserMatchTab from '@/components/LaserMatchTab'
import ConfigurationTab from '@/components/ConfigurationTab'
import ContactManager from '@/components/ContactManager'
import UsersTab from '@/components/UsersTab'

type TabType = 'lasermatch' | 'contacts' | 'users' | 'configuration'

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>('lasermatch')
  const [showRepFilter, setShowRepFilter] = useState(false)
  const [selectedReps, setSelectedReps] = useState<string[]>([])
  const [isRefreshingLaserMatch, setIsRefreshingLaserMatch] = useState(false)
  
  // This will be replaced with actual LaserMatch items data
  // For now using mock data to show the concept
  const mockItems = [
    { id: '1', assignedRep: 'Unassigned' },
    { id: '2', assignedRep: 'Unassigned' },
    { id: '3', assignedRep: 'John Smith' },
    { id: '4', assignedRep: 'John Smith' },
    { id: '5', assignedRep: 'John Smith' },
    { id: '6', assignedRep: 'Sarah Johnson' },
    { id: '7', assignedRep: 'Mike Wilson' }
  ]

  // Calculate rep counts
  const repCounts = mockItems.reduce((counts, item) => {
    const rep = item.assignedRep || 'Unassigned'
    counts[rep] = (counts[rep] || 0) + 1
    return counts
  }, {} as Record<string, number>)

  const availableReps = Object.keys(repCounts).sort((a, b) => {
    if (a === 'Unassigned') return -1
    if (b === 'Unassigned') return 1
    return a.localeCompare(b)
  })
  
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

  const refreshLaserMatchData = async () => {
    setIsRefreshingLaserMatch(true)
    try {
      const { apiService } = await import('./services/api')
      await apiService.scrapeLaserMatch()
      // The LaserMatchTab will automatically refresh its data
    } catch (error) {
      console.error('Failed to refresh LaserMatch data:', error)
    } finally {
      setIsRefreshingLaserMatch(false)
    }
  }

  const tabs = [
    { id: 'lasermatch', name: 'LaserMatch', icon: MagnifyingGlassIcon },
    { id: 'contacts', name: 'Contacts', icon: UserGroupIcon },
    { id: 'users', name: 'Users', icon: UsersIcon },
    { id: 'configuration', name: 'Configuration', icon: CogIcon },
  ]

  return (
    <div className="min-h-screen bg-black">
      {/* Header - Hidden for LaserMatch tab */}
      {activeTab !== 'lasermatch' && (
        <header className="bg-gray-900 shadow-sm border-b border-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <h1 className="text-3xl font-bold text-white">
                  Laser Equipment Intelligence
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-400">Procurement Tool</span>
              </div>
            </div>
          </div>
        </header>
      )}

      {/* Navigation Tabs */}
      <div className="bg-gray-900 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <nav className="flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as TabType)}
                    className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-white text-white'
                        : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-700'
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-2" />
                    {tab.name}
                    {tab.id === 'lasermatch' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          refreshLaserMatchData()
                        }}
                        disabled={isRefreshingLaserMatch}
                        className="ml-2 p-1 rounded hover:bg-gray-700 transition-colors"
                        title="Refresh LaserMatch data"
                      >
                        <ArrowPathIcon 
                          className={`h-4 w-4 ${isRefreshingLaserMatch ? 'animate-spin' : ''}`} 
                        />
                      </button>
                    )}
                  </button>
                )
              })}
            </nav>
            
            {/* Rep Filter - Only show on LaserMatch tab */}
            {activeTab === 'lasermatch' && (
              <div className="relative">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-400">Filter</span>
                  <button
                    onClick={() => setShowRepFilter(!showRepFilter)}
                    className="bg-gray-800 border border-gray-600 text-white px-3 py-1.5 rounded-md text-sm focus:border-gray-500 focus:outline-none flex items-center min-w-32"
                  >
                    <span className="flex-1 text-left">
                      {selectedReps.length === 0 
                        ? 'All Reps' 
                        : selectedReps.length === 1 
                          ? selectedReps[0] 
                          : `${selectedReps.length} selected`
                      }
                    </span>
                    <ChevronDownIcon className="h-4 w-4 ml-2" />
                  </button>
                  
                  {showRepFilter && (
                    <div className="absolute right-0 top-full mt-1 w-64 bg-gray-800 border border-gray-600 rounded-md shadow-lg z-50">
                      <div className="p-2 max-h-60 overflow-y-auto">
                        {availableReps.map((rep) => (
                          <label key={rep} className="flex items-center justify-between p-2 hover:bg-gray-700 rounded cursor-pointer">
                            <div className="flex items-center">
                              <input
                                type="checkbox"
                                checked={selectedReps.includes(rep)}
                                onChange={() => toggleRepFilter(rep)}
                                className="h-4 w-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                              />
                              <span className="ml-2 text-sm text-white">{rep}</span>
                            </div>
                            <span className="text-xs text-gray-400 bg-gray-700 px-2 py-0.5 rounded">
                              {repCounts[rep]}
                            </span>
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
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'lasermatch' && <LaserMatchTab selectedReps={selectedReps} />}
        {activeTab === 'contacts' && <ContactManager />}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'configuration' && <ConfigurationTab />}
      </main>
    </div>
  )
}