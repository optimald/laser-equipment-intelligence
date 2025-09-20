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

interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'manager' | 'rep'
  active: boolean
  createdAt: string
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
  const [users, setUsers] = useState<User[]>([
    {
      id: '1',
      name: 'John Smith',
      email: 'john.smith@company.com',
      role: 'admin',
      active: true,
      createdAt: '2024-01-15T10:00:00Z'
    },
    {
      id: '2',
      name: 'Sarah Johnson',
      email: 'sarah.johnson@company.com',
      role: 'manager',
      active: true,
      createdAt: '2024-01-16T14:30:00Z'
    },
    {
      id: '3',
      name: 'Mike Wilson',
      email: 'mike.wilson@company.com',
      role: 'rep',
      active: true,
      createdAt: '2024-01-17T09:15:00Z'
    },
    {
      id: '4',
      name: 'Lisa Brown',
      email: 'lisa.brown@company.com',
      role: 'rep',
      active: false,
      createdAt: '2024-01-10T16:45:00Z'
    }
  ])
  const [isLoading, setIsLoading] = useState(true)
  const [isAddingUser, setIsAddingUser] = useState(false)
  const [editingUser, setEditingUser] = useState<string | null>(null)
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'rep' as 'admin' | 'manager' | 'rep'
  })

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

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-purple-100 text-purple-800'
      case 'manager': return 'bg-blue-100 text-blue-800'
      case 'rep': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const addUser = () => {
    if (!newUser.name.trim() || !newUser.email.trim()) return

    const user: User = {
      id: Date.now().toString(),
      name: newUser.name.trim(),
      email: newUser.email.trim(),
      role: newUser.role,
      active: true,
      createdAt: new Date().toISOString()
    }

    setUsers(prev => [user, ...prev])
    setNewUser({ name: '', email: '', role: 'rep' })
    setIsAddingUser(false)
  }

  const updateUser = (userId: string, updates: Partial<User>) => {
    setUsers(prev => prev.map(user => 
      user.id === userId ? { ...user, ...updates } : user
    ))
  }

  const deleteUser = (userId: string) => {
    if (confirm('Are you sure you want to delete this user?')) {
      setUsers(prev => prev.filter(user => user.id !== userId))
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

      {/* User Management */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-lg font-medium text-gray-900">User Management</h3>
            <p className="text-sm text-gray-600">Manage users who can be assigned to procurement tasks</p>
          </div>
          <button
            onClick={() => setIsAddingUser(true)}
            className="btn-primary"
          >
            Add User
          </button>
        </div>

        {/* Add User Form */}
        {isAddingUser && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h4 className="text-md font-medium text-gray-900 mb-3">Add New User</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <input
                type="text"
                placeholder="Full name *"
                value={newUser.name}
                onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
                className="input-field"
              />
              <input
                type="email"
                placeholder="Email address *"
                value={newUser.email}
                onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                className="input-field"
              />
              <select
                value={newUser.role}
                onChange={(e) => setNewUser(prev => ({ ...prev, role: e.target.value as 'admin' | 'manager' | 'rep' }))}
                className="input-field"
              >
                <option value="rep">Rep</option>
                <option value="manager">Manager</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => {
                  setIsAddingUser(false)
                  setNewUser({ name: '', email: '', role: 'rep' })
                }}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={addUser}
                disabled={!newUser.name.trim() || !newUser.email.trim()}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Add User
              </button>
            </div>
          </div>
        )}

        {/* Users Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{user.name}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor(user.role)}`}>
                      {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.createdAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => updateUser(user.id, { active: !user.active })}
                        className={`text-xs px-3 py-1 rounded ${
                          user.active 
                            ? 'text-red-600 hover:text-red-700' 
                            : 'text-green-600 hover:text-green-700'
                        }`}
                      >
                        {user.active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        onClick={() => deleteUser(user.id)}
                        className="text-xs text-red-600 hover:text-red-700 px-3 py-1 rounded"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {users.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No users configured. Click "Add User" to get started.</p>
          </div>
        )}
      </div>
    </div>
  )
}
