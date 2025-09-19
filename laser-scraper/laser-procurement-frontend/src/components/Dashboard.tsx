'use client'

import { useState, useEffect } from 'react'
import {
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  EyeIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface DashboardStats {
  totalListings: number
  newListings: number
  highValueListings: number
  avgMargin: number
  topSources: Array<{
    name: string
    count: number
    percentage: number
  }>
  recentActivity: Array<{
    id: string
    action: string
    item: string
    timestamp: string
    source: string
  }>
  priceTrends: Array<{
    date: string
    avgPrice: number
    count: number
  }>
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Mock data for demonstration
  useEffect(() => {
    const mockStats: DashboardStats = {
      totalListings: 1247,
      newListings: 89,
      highValueListings: 23,
      avgMargin: 28.5,
      topSources: [
        { name: 'LaserMatch.io', count: 234, percentage: 18.8 },
        { name: 'DOTmed Auctions', count: 198, percentage: 15.9 },
        { name: 'BidSpotter', count: 156, percentage: 12.5 },
        { name: 'The Laser Warehouse', count: 134, percentage: 10.7 },
        { name: 'Laser Agent', count: 112, percentage: 9.0 },
        { name: 'eBay', count: 98, percentage: 7.9 },
        { name: 'Iron Horse Auction', count: 87, percentage: 7.0 },
        { name: 'Kurtz Auction', count: 76, percentage: 6.1 },
        { name: 'Other Sources', count: 152, percentage: 12.2 }
      ],
      recentActivity: [
        {
          id: '1',
          action: 'New listing discovered',
          item: 'Sciton Joule Laser System',
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          source: 'LaserMatch.io'
        },
        {
          id: '2',
          action: 'High-value alert triggered',
          item: 'Cynosure PicoSure Pro',
          timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
          source: 'DOTmed Auctions'
        },
        {
          id: '3',
          action: 'Listing updated',
          item: 'Cutera Excel V System',
          timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
          source: 'BidSpotter'
        },
        {
          id: '4',
          action: 'Auction ending soon',
          item: 'Lumenis M22 IPL',
          timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
          source: 'Iron Horse Auction'
        },
        {
          id: '5',
          action: 'New listing discovered',
          item: 'Alma Harmony XL Pro',
          timestamp: new Date(Date.now() - 67 * 60 * 1000).toISOString(),
          source: 'The Laser Warehouse'
        }
      ],
      priceTrends: [
        { date: '2024-01-01', avgPrice: 85000, count: 45 },
        { date: '2024-01-02', avgPrice: 87000, count: 52 },
        { date: '2024-01-03', avgPrice: 82000, count: 38 },
        { date: '2024-01-04', avgPrice: 89000, count: 61 },
        { date: '2024-01-05', avgPrice: 91000, count: 47 },
        { date: '2024-01-06', avgPrice: 88000, count: 43 },
        { date: '2024-01-07', avgPrice: 92000, count: 55 }
      ]
    }

    setTimeout(() => {
      setStats(mockStats)
      setIsLoading(false)
    }, 1000)
  }, [])

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price)
  }

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return `${Math.floor(diffMins / 1440)}d ago`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading dashboard...</span>
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Listings</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalListings.toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm text-green-600">
            <TrendingUpIcon className="h-4 w-4 mr-1" />
            <span>+{stats.newListings} new today</span>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <EyeIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">High-Value Listings</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.highValueListings}</p>
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm text-yellow-600">
            <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
            <span>Requires attention</span>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avg. Margin</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.avgMargin}%</p>
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm text-green-600">
            <TrendingUpIcon className="h-4 w-4 mr-1" />
            <span>+2.3% vs last week</span>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Last Update</p>
              <p className="text-2xl font-semibold text-gray-900">5m ago</p>
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm text-green-600">
            <CheckCircleIcon className="h-4 w-4 mr-1" />
            <span>All systems active</span>
          </div>
        </div>
      </div>

      {/* Charts and Data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Sources */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Data Sources</h3>
          <div className="space-y-3">
            {stats.topSources.map((source, index) => (
              <div key={source.name} className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-sm font-medium text-gray-500 w-6">{index + 1}.</span>
                  <span className="text-sm font-medium text-gray-900 ml-2">{source.name}</span>
                </div>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div 
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${source.percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-500 w-12 text-right">
                    {source.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Price Trends */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Price Trends (7 Days)</h3>
          <div className="space-y-3">
            {stats.priceTrends.map((trend, index) => {
              const prevTrend = index > 0 ? stats.priceTrends[index - 1] : null
              const priceChange = prevTrend ? trend.avgPrice - prevTrend.avgPrice : 0
              
              return (
                <div key={trend.date} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(trend.date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </p>
                    <p className="text-xs text-gray-500">{trend.count} listings</p>
                  </div>
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-900 mr-2">
                      {formatPrice(trend.avgPrice)}
                    </span>
                    {priceChange !== 0 && (
                      <span className={`text-xs flex items-center ${
                        priceChange > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {priceChange > 0 ? (
                          <TrendingUpIcon className="h-3 w-3 mr-1" />
                        ) : (
                          <TrendingDownIcon className="h-3 w-3 mr-1" />
                        )}
                        {Math.abs(priceChange / 1000).toFixed(1)}k
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {stats.recentActivity.map((activity) => (
            <div key={activity.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-2 w-2 bg-primary-600 rounded-full"></div>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">
                    {activity.action}
                  </p>
                  <p className="text-sm text-gray-500">
                    {activity.item} • {activity.source}
                  </p>
                </div>
              </div>
              <div className="text-sm text-gray-500">
                {formatTimeAgo(activity.timestamp)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
