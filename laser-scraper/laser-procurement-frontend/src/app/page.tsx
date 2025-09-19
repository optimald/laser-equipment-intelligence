'use client'

import { useState, useEffect } from 'react'
import { MagnifyingGlassIcon, CogIcon, ChartBarIcon, BoltIcon } from '@heroicons/react/24/outline'
import EquipmentSearch from '@/components/EquipmentSearch'
import SourceConfiguration from '@/components/SourceConfiguration'
import SearchResults from '@/components/SearchResults'
import Dashboard from '@/components/Dashboard'

type TabType = 'search' | 'configuration' | 'dashboard'

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>('search')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [isSearching, setIsSearching] = useState(false)

  const tabs = [
    { id: 'search', name: 'Equipment Search', icon: MagnifyingGlassIcon },
    { id: 'configuration', name: 'Source Configuration', icon: CogIcon },
    { id: 'dashboard', name: 'Dashboard', icon: ChartBarIcon },
  ]

  const handleSearch = async (searchParams: any) => {
    setIsSearching(true)
    try {
      console.log('Searching with params:', searchParams)
      
      // Import the API service dynamically to avoid SSR issues
      const { apiService } = await import('../services/api')
      
      const results = await apiService.searchEquipment(searchParams)
      setSearchResults(results)
    } catch (error) {
      console.error('Search failed:', error)
      // Fallback to mock data if API fails
      const mockResults = [
        {
          id: 1,
          title: 'Sciton Joule Laser System',
          brand: 'Sciton',
          model: 'Joule',
          condition: 'excellent',
          price: 85000,
          source: 'LaserMatch.io',
          location: 'California, USA',
          description: 'Complete Sciton Joule laser system with multiple handpieces',
          images: ['/placeholder-equipment.jpg'],
          discovered_at: new Date().toISOString(),
          margin_estimate: 25000,
          score_overall: 85
        },
        {
          id: 2,
          title: 'Cynosure PicoSure Pro',
          brand: 'Cynosure',
          model: 'PicoSure Pro',
          condition: 'good',
          price: 120000,
          source: 'DOTmed Auctions',
          location: 'Texas, USA',
          description: 'Cynosure PicoSure Pro tattoo removal laser',
          images: ['/placeholder-equipment.jpg'],
          discovered_at: new Date().toISOString(),
          margin_estimate: 30000,
          score_overall: 78
        }
      ]
      
      setSearchResults(mockResults)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <BoltIcon className="h-8 w-8 text-primary-600" />
              <h1 className="ml-2 text-xl font-semibold text-gray-900">
                Laser Procurement Intelligence
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {tab.name}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'search' && (
          <div className="space-y-8">
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Equipment Search
              </h2>
              <EquipmentSearch onSearch={handleSearch} isSearching={isSearching} />
            </div>
            
            {searchResults.length > 0 && (
              <SearchResults results={searchResults} />
            )}
          </div>
        )}

        {activeTab === 'configuration' && (
          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Source Configuration
            </h2>
            <SourceConfiguration />
          </div>
        )}

        {activeTab === 'dashboard' && (
          <Dashboard />
        )}
      </main>
    </div>
  )
}
