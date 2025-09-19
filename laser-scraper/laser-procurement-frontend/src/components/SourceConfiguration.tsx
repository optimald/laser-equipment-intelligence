'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { 
  CogIcon, 
  PlayIcon, 
  PauseIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'

interface SourceConfig {
  id: string
  name: string
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  enabled: boolean
  crawlFrequency: number // hours
  maxConcurrent: number
  delayMin: number // seconds
  delayMax: number // seconds
  evasionLevel: 'LOW' | 'MEDIUM' | 'HIGH'
  lastCrawl?: string
  status: 'ACTIVE' | 'PAUSED' | 'ERROR' | 'OFFLINE'
  successRate: number
}

interface SourceConfigurationProps {}

export default function SourceConfiguration({}: SourceConfigurationProps) {
  const [sources, setSources] = useState<SourceConfig[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedSource, setSelectedSource] = useState<SourceConfig | null>(null)

  // Mock data for demonstration
  useEffect(() => {
    const mockSources: SourceConfig[] = [
      {
        id: 'lasermatch',
        name: 'LaserMatch.io',
        priority: 'HIGH',
        enabled: true,
        crawlFrequency: 1,
        maxConcurrent: 8,
        delayMin: 2,
        delayMax: 5,
        evasionLevel: 'LOW',
        lastCrawl: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 95
      },
      {
        id: 'dotmed',
        name: 'DOTmed Auctions',
        priority: 'HIGH',
        enabled: true,
        crawlFrequency: 2,
        maxConcurrent: 4,
        delayMin: 3,
        delayMax: 8,
        evasionLevel: 'HIGH',
        lastCrawl: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 88
      },
      {
        id: 'bidspotter',
        name: 'BidSpotter',
        priority: 'HIGH',
        enabled: true,
        crawlFrequency: 4,
        maxConcurrent: 6,
        delayMin: 2,
        delayMax: 6,
        evasionLevel: 'MEDIUM',
        lastCrawl: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 92
      },
      {
        id: 'ebay',
        name: 'eBay',
        priority: 'MEDIUM',
        enabled: true,
        crawlFrequency: 6,
        maxConcurrent: 2,
        delayMin: 5,
        delayMax: 15,
        evasionLevel: 'HIGH',
        lastCrawl: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 78
      },
      {
        id: 'facebook',
        name: 'Facebook Marketplace',
        priority: 'LOW',
        enabled: false,
        crawlFrequency: 12,
        maxConcurrent: 1,
        delayMin: 60,
        delayMax: 120,
        evasionLevel: 'HIGH',
        lastCrawl: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        status: 'PAUSED',
        successRate: 65
      },
      {
        id: 'craigslist',
        name: 'Craigslist',
        priority: 'LOW',
        enabled: false,
        crawlFrequency: 24,
        maxConcurrent: 2,
        delayMin: 30,
        delayMax: 60,
        evasionLevel: 'HIGH',
        lastCrawl: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
        status: 'OFFLINE',
        successRate: 45
      },
      {
        id: 'thelaserwarehouse',
        name: 'The Laser Warehouse',
        priority: 'HIGH',
        enabled: true,
        crawlFrequency: 2,
        maxConcurrent: 6,
        delayMin: 2,
        delayMax: 5,
        evasionLevel: 'LOW',
        lastCrawl: new Date(Date.now() - 90 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 97
      },
      {
        id: 'laser_agent',
        name: 'Laser Agent',
        priority: 'HIGH',
        enabled: true,
        crawlFrequency: 3,
        maxConcurrent: 6,
        delayMin: 2,
        delayMax: 5,
        evasionLevel: 'LOW',
        lastCrawl: new Date(Date.now() - 120 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 94
      },
      {
        id: 'iron_horse',
        name: 'Iron Horse Auction',
        priority: 'HIGH',
        enabled: true,
        crawlFrequency: 4,
        maxConcurrent: 8,
        delayMin: 3,
        delayMax: 8,
        evasionLevel: 'MEDIUM',
        lastCrawl: new Date(Date.now() - 180 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 89
      },
      {
        id: 'kurtz',
        name: 'Kurtz Auction',
        priority: 'HIGH',
        enabled: true,
        crawlFrequency: 4,
        maxConcurrent: 10,
        delayMin: 2,
        delayMax: 6,
        evasionLevel: 'MEDIUM',
        lastCrawl: new Date(Date.now() - 150 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 91
      },
      {
        id: 'asset_recovery',
        name: 'Asset Recovery Services',
        priority: 'HIGH',
        enabled: true,
        crawlFrequency: 6,
        maxConcurrent: 10,
        delayMin: 2,
        delayMax: 6,
        evasionLevel: 'MEDIUM',
        lastCrawl: new Date(Date.now() - 200 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 87
      },
      {
        id: 'hilditch',
        name: 'Hilditch Group (EU/UK)',
        priority: 'MEDIUM',
        enabled: true,
        crawlFrequency: 8,
        maxConcurrent: 8,
        delayMin: 3,
        delayMax: 8,
        evasionLevel: 'MEDIUM',
        lastCrawl: new Date(Date.now() - 240 * 60 * 1000).toISOString(),
        status: 'ACTIVE',
        successRate: 83
      }
    ]

    setTimeout(() => {
      setSources(mockSources)
      setIsLoading(false)
    }, 1000)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'PAUSED':
        return <PauseIcon className="h-5 w-5 text-yellow-500" />
      case 'ERROR':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
      case 'OFFLINE':
        return <InformationCircleIcon className="h-5 w-5 text-gray-500" />
      default:
        return <InformationCircleIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'badge-success'
      case 'PAUSED': return 'badge-warning'
      case 'ERROR': return 'badge-error'
      case 'OFFLINE': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH': return 'badge-error'
      case 'MEDIUM': return 'badge-warning'
      case 'LOW': return 'badge-success'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const toggleSource = (id: string) => {
    setSources(prev => prev.map(source => 
      source.id === id 
        ? { ...source, enabled: !source.enabled, status: !source.enabled ? 'ACTIVE' : 'PAUSED' }
        : source
    ))
  }

  const formatLastCrawl = (lastCrawl: string) => {
    const date = new Date(lastCrawl)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 60) {
      return `${diffMins}m ago`
    } else if (diffMins < 1440) {
      return `${Math.floor(diffMins / 60)}h ago`
    } else {
      return `${Math.floor(diffMins / 1440)}d ago`
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading source configuration...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Global Controls */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Global Controls</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="btn-primary flex items-center justify-center">
            <PlayIcon className="h-4 w-4 mr-2" />
            Start All Sources
          </button>
          <button className="btn-secondary flex items-center justify-center">
            <PauseIcon className="h-4 w-4 mr-2" />
            Pause All Sources
          </button>
          <button className="btn-secondary flex items-center justify-center">
            <CogIcon className="h-4 w-4 mr-2" />
            Global Settings
          </button>
        </div>
      </div>

      {/* Sources List */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Data Sources</h3>
        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Frequency
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Crawl
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sources.map((source) => (
                <tr key={source.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={source.enabled}
                        onChange={() => toggleSource(source.id)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">
                          {source.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {source.maxConcurrent} concurrent • {source.delayMin}-{source.delayMax}s delay
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(source.status)}
                      <span className={`ml-2 badge ${getStatusColor(source.status)}`}>
                        {source.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${getPriorityColor(source.priority)}`}>
                      {source.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    Every {source.crawlFrequency}h
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className={`h-2 rounded-full ${
                            source.successRate >= 90 ? 'bg-green-500' :
                            source.successRate >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${source.successRate}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">{source.successRate}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {source.lastCrawl ? formatLastCrawl(source.lastCrawl) : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setSelectedSource(source)}
                      className="text-primary-600 hover:text-primary-900 mr-4"
                    >
                      Configure
                    </button>
                    <button className="text-gray-600 hover:text-gray-900">
                      View Logs
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Source Details Modal */}
      {selectedSource && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Configure {selectedSource.name}
              </h3>
              
              <form className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Crawl Frequency (hours)
                    </label>
                    <input
                      type="number"
                      defaultValue={selectedSource.crawlFrequency}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Concurrent Requests
                    </label>
                    <input
                      type="number"
                      defaultValue={selectedSource.maxConcurrent}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Min Delay (seconds)
                    </label>
                    <input
                      type="number"
                      defaultValue={selectedSource.delayMin}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Delay (seconds)
                    </label>
                    <input
                      type="number"
                      defaultValue={selectedSource.delayMax}
                      className="input-field"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Evasion Level
                    </label>
                    <select defaultValue={selectedSource.evasionLevel} className="input-field">
                      <option value="LOW">Low (Government sites)</option>
                      <option value="MEDIUM">Medium (Auction sites)</option>
                      <option value="HIGH">High (Marketplaces)</option>
                    </select>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setSelectedSource(null)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    Save Configuration
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
