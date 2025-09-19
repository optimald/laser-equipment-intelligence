'use client'

import { useState } from 'react'
import { 
  EyeIcon, 
  HeartIcon, 
  ShareIcon, 
  CurrencyDollarIcon,
  MapPinIcon,
  CalendarIcon,
  TagIcon,
  StarIcon
} from '@heroicons/react/24/outline'
import { HeartIcon as HeartSolidIcon, StarIcon as StarSolidIcon } from '@heroicons/react/24/solid'

interface SearchResult {
  id: string
  title: string
  brand: string
  model: string
  condition: string
  price: number
  source: string
  location: string
  description: string
  images: string[]
  discovered_at: string
  margin_estimate?: number
  score_overall?: number
}

interface SearchResultsProps {
  results: SearchResult[]
}

export default function SearchResults({ results }: SearchResultsProps) {
  const [favorites, setFavorites] = useState<Set<string>>(new Set())
  const [sortBy, setSortBy] = useState<'relevance' | 'price' | 'score' | 'date'>('relevance')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const toggleFavorite = (id: string) => {
    const newFavorites = new Set(favorites)
    if (newFavorites.has(id)) {
      newFavorites.delete(id)
    } else {
      newFavorites.add(id)
    }
    setFavorites(newFavorites)
  }

  const getConditionColor = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'excellent': return 'badge-success'
      case 'good': return 'badge-success'
      case 'fair': return 'badge-warning'
      case 'poor': return 'badge-error'
      case 'refurbished': return 'badge-warning'
      default: return 'badge-secondary'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const sortedResults = [...results].sort((a, b) => {
    switch (sortBy) {
      case 'price':
        return a.price - b.price
      case 'score':
        return (b.score_overall || 0) - (a.score_overall || 0)
      case 'date':
        return new Date(b.discovered_at).getTime() - new Date(a.discovered_at).getTime()
      default:
        return (b.score_overall || 0) - (a.score_overall || 0)
    }
  })

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-medium text-gray-900">
            Search Results
          </h2>
          <p className="text-sm text-gray-500">
            {results.length} equipment items found
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="input-field w-auto"
          >
            <option value="relevance">Sort by Relevance</option>
            <option value="score">Sort by Score</option>
            <option value="price">Sort by Price</option>
            <option value="date">Sort by Date</option>
          </select>
          
          {/* View Mode */}
          <div className="flex rounded-md shadow-sm">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 text-sm font-medium rounded-l-md border ${
                viewMode === 'grid'
                  ? 'bg-primary-50 border-primary-500 text-primary-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 text-sm font-medium rounded-r-md border-t border-r border-b ${
                viewMode === 'list'
                  ? 'bg-primary-50 border-primary-500 text-primary-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              List
            </button>
          </div>
        </div>
      </div>

      {/* Results Grid/List */}
      <div className={viewMode === 'grid' 
        ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
        : 'space-y-4'
      }>
        {sortedResults.map((item) => (
          <div key={item.id} className={`card hover:shadow-md transition-shadow ${
            viewMode === 'list' ? 'flex' : ''
          }`}>
            {viewMode === 'grid' ? (
              // Grid View
              <>
                <div className="aspect-w-16 aspect-h-9 mb-4">
                  <img
                    src={item.images[0] || '/placeholder-equipment.jpg'}
                    alt={item.title}
                    className="w-full h-48 object-cover rounded-lg"
                  />
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900 line-clamp-2">
                        {item.title}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {item.brand} {item.model}
                      </p>
                    </div>
                    <button
                      onClick={() => toggleFavorite(item.id)}
                      className="p-1 text-gray-400 hover:text-red-500"
                    >
                      {favorites.has(item.id) ? (
                        <HeartSolidIcon className="h-5 w-5 text-red-500" />
                      ) : (
                        <HeartIcon className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-gray-900">
                      {formatPrice(item.price)}
                    </span>
                    {item.score_overall && (
                      <div className="flex items-center">
                        <StarSolidIcon className="h-4 w-4 text-yellow-400 mr-1" />
                        <span className={`text-sm font-medium ${getScoreColor(item.score_overall)}`}>
                          {item.score_overall}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`badge ${getConditionColor(item.condition)}`}>
                      {item.condition}
                    </span>
                    <span className="badge bg-blue-100 text-blue-800">
                      {item.source}
                    </span>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-500">
                    <MapPinIcon className="h-4 w-4 mr-1" />
                    {item.location}
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-sm text-gray-500">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      {formatDate(item.discovered_at)}
                    </div>
                    <button className="btn-primary text-sm py-1 px-3">
                      View Details
                    </button>
                  </div>
                </div>
              </>
            ) : (
              // List View
              <>
                <div className="w-32 h-24 flex-shrink-0">
                  <img
                    src={item.images[0] || '/placeholder-equipment.jpg'}
                    alt={item.title}
                    className="w-full h-full object-cover rounded-lg"
                  />
                </div>
                
                <div className="flex-1 ml-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">
                        {item.title}
                      </h3>
                      <p className="text-sm text-gray-500 mb-2">
                        {item.brand} {item.model} • {item.source}
                      </p>
                      <p className="text-sm text-gray-700 line-clamp-2">
                        {item.description}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => toggleFavorite(item.id)}
                        className="p-1 text-gray-400 hover:text-red-500"
                      >
                        {favorites.has(item.id) ? (
                          <HeartSolidIcon className="h-5 w-5 text-red-500" />
                        ) : (
                          <HeartIcon className="h-5 w-5" />
                        )}
                      </button>
                      <button className="p-1 text-gray-400 hover:text-gray-600">
                        <ShareIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-4">
                    <div className="flex items-center space-x-4">
                      <span className="text-xl font-bold text-gray-900">
                        {formatPrice(item.price)}
                      </span>
                      {item.margin_estimate && (
                        <span className="text-sm text-green-600">
                          Est. Margin: {formatPrice(item.margin_estimate)}
                        </span>
                      )}
                      {item.score_overall && (
                        <div className="flex items-center">
                          <StarSolidIcon className="h-4 w-4 text-yellow-400 mr-1" />
                          <span className={`text-sm font-medium ${getScoreColor(item.score_overall)}`}>
                            {item.score_overall}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className={`badge ${getConditionColor(item.condition)}`}>
                        {item.condition}
                      </span>
                      <div className="flex items-center text-sm text-gray-500">
                        <MapPinIcon className="h-4 w-4 mr-1" />
                        {item.location}
                      </div>
                      <button className="btn-primary text-sm py-1 px-3">
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      {/* Load More */}
      {results.length > 0 && (
        <div className="text-center">
          <button className="btn-secondary">
            Load More Results
          </button>
        </div>
      )}
    </div>
  )
}
