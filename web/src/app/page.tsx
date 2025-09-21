'use client'

import { useState } from 'react'
import { MagnifyingGlassIcon, CogIcon, UserGroupIcon, UsersIcon } from '@heroicons/react/24/outline'
import LaserMatchTab from '@/components/LaserMatchTab'
import ConfigurationTab from '@/components/ConfigurationTab'
import ContactManager from '@/components/ContactManager'
import UsersTab from '@/components/UsersTab'

type TabType = 'lasermatch' | 'contacts' | 'users' | 'configuration'

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>('lasermatch')

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
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'lasermatch' && <LaserMatchTab />}
        {activeTab === 'contacts' && <ContactManager />}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'configuration' && <ConfigurationTab />}
      </main>
    </div>
  )
}