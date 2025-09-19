'use client'

import { useState } from 'react'
import { MagnifyingGlassIcon, CogIcon } from '@heroicons/react/24/outline'
import LaserMatchTab from '@/components/LaserMatchTab'
import ConfigurationTab from '@/components/ConfigurationTab'

type TabType = 'lasermatch' | 'configuration'

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>('lasermatch')

  const tabs = [
    { id: 'lasermatch', name: 'LaserMatch', icon: MagnifyingGlassIcon },
    { id: 'configuration', name: 'Configuration', icon: CogIcon },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">
                Laser Equipment Intelligence
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Procurement Tool</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
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
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'lasermatch' && <LaserMatchTab />}
        {activeTab === 'configuration' && <ConfigurationTab />}
      </main>
    </div>
  )
}