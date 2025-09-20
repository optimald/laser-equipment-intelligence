'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'

interface SourceConfig {
  id: string
  name: string
  enabled: boolean
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  defaultSearchCount: number
  delay: number // seconds between requests
}

interface SearchConfig {
  defaultSources: string[]
  defaultSearchCount: number
  maxConcurrentSearches: number
  searchTimeout: number // seconds
  autoRefresh: boolean
  refreshInterval: number // minutes
}


export default function ConfigurationTab() {
  const [sources, setSources] = useState<SourceConfig[]>([])
  const [searchConfig, setSearchConfig] = useState<SearchConfig>({
    defaultSources: ['DOTmed Auctions', 'eBay', 'BidSpotter'],
    defaultSearchCount: 5,
    maxConcurrentSearches: 3,
    searchTimeout: 30,
    autoRefresh: false,
    refreshInterval: 60
  })
  const [isLoading, setIsLoading] = useState(true)

  const { register, handleSubmit, watch, setValue } = useForm<SearchConfig>()

  // Load configuration on mount
  useEffect(() => {
    loadConfiguration()
  }, [])

  const loadConfiguration = async () => {
    setIsLoading(true)
    try {
      const { apiService } = await import('../services/api')
      const apiSources = await apiService.getSourceConfigurations()
      
      // Convert API response to component interface
      const convertedSources: SourceConfig[] = apiSources.map(source => ({
        id: source.id,
        name: source.name,
        enabled: source.enabled,
        priority: source.priority as 'HIGH' | 'MEDIUM' | 'LOW',
        defaultSearchCount: source.priority === 'HIGH' ? 10 : source.priority === 'MEDIUM' ? 5 : 3,
        delay: source.priority === 'HIGH' ? 2 : source.priority === 'MEDIUM' ? 5 : 10
      }))
      
      setSources(convertedSources)
      
      // Set form values
      setValue('defaultSources', searchConfig.defaultSources)
      setValue('defaultSearchCount', searchConfig.defaultSearchCount)
      setValue('maxConcurrentSearches', searchConfig.maxConcurrentSearches)
      setValue('searchTimeout', searchConfig.searchTimeout)
      setValue('autoRefresh', searchConfig.autoRefresh)
      setValue('refreshInterval', searchConfig.refreshInterval)
    } catch (error) {
      console.error('Failed to load configuration:', error)
      setSources([])
    } finally {
      setIsLoading(false)
    }
  }

  const updateSource = async (sourceId: string, enabled: boolean) => {
    try {
      const { apiService } = await import('../services/api')
      await apiService.updateSourceConfiguration(sourceId, enabled)
      
      setSources(prev => prev.map(source => 
        source.id === sourceId ? { ...source, enabled } : source
      ))
    } catch (error) {
      console.error('Failed to update source:', error)
    }
  }

  const onSubmit = async (data: SearchConfig) => {
    try {
      // Save configuration to API
      setSearchConfig(data)
      console.log('Configuration saved:', data)
      // TODO: Implement API call to save configuration
    } catch (error) {
      console.error('Failed to save configuration:', error)
    }
  }

  const runAllSpiders = async () => {
    try {
      const { apiService } = await import('../services/api')
      await apiService.runAllSpiders()
      console.log('All spiders started')
    } catch (error) {
      console.error('Failed to run spiders:', error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH': return 'bg-red-100 text-red-800'
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800'
      case 'LOW': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }


  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading configuration...</span>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Configuration</h2>
        <p className="text-gray-600">Configure search sources, defaults, and system settings</p>
      </div>

      {/* Search Configuration */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Search Settings</h3>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Search Count
              </label>
              <input
                {...register('defaultSearchCount', { valueAsNumber: true })}
                type="number"
                min="1"
                max="50"
                className="input-field"
              />
              <p className="text-sm text-gray-500 mt-1">
                Number of items to search for per source
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Concurrent Searches
              </label>
              <input
                {...register('maxConcurrentSearches', { valueAsNumber: true })}
                type="number"
                min="1"
                max="10"
                className="input-field"
              />
              <p className="text-sm text-gray-500 mt-1">
                Maximum number of simultaneous source searches
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Timeout (seconds)
              </label>
              <input
                {...register('searchTimeout', { valueAsNumber: true })}
                type="number"
                min="10"
                max="300"
                className="input-field"
              />
              <p className="text-sm text-gray-500 mt-1">
                Maximum time to wait for each source search
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Auto Refresh Interval (minutes)
              </label>
              <input
                {...register('refreshInterval', { valueAsNumber: true })}
                type="number"
                min="5"
                max="1440"
                className="input-field"
              />
              <p className="text-sm text-gray-500 mt-1">
                How often to automatically refresh equipment items
              </p>
            </div>
          </div>

          <div className="flex items-center">
            <input
              {...register('autoRefresh')}
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              Enable auto-refresh of equipment items
            </label>
          </div>

          <button type="submit" className="btn-primary">
            Save Configuration
          </button>
        </form>
      </div>

      {/* Data Sources */}
      <div className="card">
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-900">Data Sources</h3>
        </div>

        <div className="space-y-6">
          {/* Show all sources grouped by category */}
          {sources.length > 0 ? (
            <>
              {/* Auction & Liquidation Platforms */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Auction & Liquidation Platforms</h4>
                <div className="space-y-3">
                  {sources.filter(s => 
                    s.name.toLowerCase().includes('auction') || 
                    s.name.toLowerCase().includes('bid') ||
                    s.name.toLowerCase().includes('gov') ||
                    s.name.toLowerCase().includes('heritage') ||
                    s.name.toLowerCase().includes('iron horse') ||
                    s.name.toLowerCase().includes('kurtz') ||
                    s.name.toLowerCase().includes('centurion')
                  ).map((source) => (
                    <div key={source.id} className="flex items-center p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-4 flex-1">
                        <input
                          type="checkbox"
                          checked={source.enabled}
                          onChange={(e) => updateSource(source.id, e.target.checked)}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <div className="flex-1">
                          <h4 className="text-base font-medium text-gray-900">{source.name}</h4>
                          <div className="flex items-center space-x-3 mt-1">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(source.priority)}`}>
                              {source.priority}
                            </span>
                            <span className="text-sm text-gray-500">
                              {source.defaultSearchCount} items • {source.delay}s delay
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Dealer / Liquidator / Repossession */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Dealer / Liquidator / Repossession</h4>
                <div className="space-y-3">
                  {sources.filter(s => 
                    s.name.toLowerCase().includes('asset') ||
                    s.name.toLowerCase().includes('recovery') ||
                    s.name.toLowerCase().includes('repo') ||
                    s.name.toLowerCase().includes('liquidator') ||
                    s.name.toLowerCase().includes('medical') ||
                    s.name.toLowerCase().includes('healthcare') ||
                    s.name.toLowerCase().includes('alliance') ||
                    s.name.toLowerCase().includes('southeast')
                  ).map((source) => (
                    <div key={source.id} className="flex items-center p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-4 flex-1">
                        <input
                          type="checkbox"
                          checked={source.enabled}
                          onChange={(e) => updateSource(source.id, e.target.checked)}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <div className="flex-1">
                          <h4 className="text-base font-medium text-gray-900">{source.name}</h4>
                          <div className="flex items-center space-x-3 mt-1">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(source.priority)}`}>
                              {source.priority}
                            </span>
                            <span className="text-sm text-gray-500">
                              {source.defaultSearchCount} items • {source.delay}s delay
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Marketplaces / Classifieds */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Marketplaces / Classifieds</h4>
                <div className="space-y-3">
                  {sources.filter(s => 
                    s.name.toLowerCase().includes('ebay') ||
                    s.name.toLowerCase().includes('facebook') ||
                    s.name.toLowerCase().includes('craigslist') ||
                    s.name.toLowerCase().includes('labx') ||
                    s.name.toLowerCase().includes('used-line') ||
                    s.name.toLowerCase().includes('marketplace')
                  ).map((source) => (
                    <div key={source.id} className="flex items-center p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-4 flex-1">
                        <input
                          type="checkbox"
                          checked={source.enabled}
                          onChange={(e) => updateSource(source.id, e.target.checked)}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <div className="flex-1">
                          <h4 className="text-base font-medium text-gray-900">{source.name}</h4>
                          <div className="flex items-center space-x-3 mt-1">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(source.priority)}`}>
                              {source.priority}
                            </span>
                            <span className="text-sm text-gray-500">
                              {source.defaultSearchCount} items • {source.delay}s delay
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Notices / Financial Signals */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Notices / Financial Signals</h4>
                <div className="space-y-3">
                  {sources.filter(s => 
                    s.name.toLowerCase().includes('fdic') ||
                    s.name.toLowerCase().includes('naam') ||
                    s.name.toLowerCase().includes('ner') ||
                    s.name.toLowerCase().includes('bank') ||
                    s.name.toLowerCase().includes('theft') ||
                    s.name.toLowerCase().includes('financial')
                  ).map((source) => (
                    <div key={source.id} className="flex items-center p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-4 flex-1">
                        <input
                          type="checkbox"
                          checked={source.enabled}
                          onChange={(e) => updateSource(source.id, e.target.checked)}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <div className="flex-1">
                          <h4 className="text-base font-medium text-gray-900">{source.name}</h4>
                          <div className="flex items-center space-x-3 mt-1">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(source.priority)}`}>
                              {source.priority}
                            </span>
                            <span className="text-sm text-gray-500">
                              {source.defaultSearchCount} items • {source.delay}s delay
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">No data sources available. Please check your API connection.</p>
            </div>
          )}
        </div>
      </div>

      {/* System Status */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {sources.filter(s => s.enabled).length}
            </div>
            <div className="text-sm text-green-700">Active Sources</div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {sources.filter(s => s.priority === 'HIGH' && s.enabled).length}
            </div>
            <div className="text-sm text-blue-700">High Priority</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {searchConfig.maxConcurrentSearches}
            </div>
            <div className="text-sm text-purple-700">Max Concurrent</div>
          </div>
        </div>
      </div>

    </div>
  )
}
