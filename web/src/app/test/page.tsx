'use client';

import React, { useState, useEffect } from 'react';

export default function TestPage() {
  const [apiStatus, setApiStatus] = useState<string>('Testing...');
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState<string>('');

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const testAPI = async () => {
      try {
        // Test health endpoint
        const healthResponse = await fetch(`${API_BASE_URL}/health`);
        const healthData = await healthResponse.json();
        setApiStatus(`API Health: ${healthData.status}`);

        // Test items endpoint
        const itemsResponse = await fetch(`${API_BASE_URL}/api/v1/lasermatch/items`);
        const itemsData = await itemsResponse.json();
        setItems(itemsData.items || []);
        setError('');
      } catch (err) {
        setError(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
        setApiStatus('API Connection Failed');
      }
    };

    testAPI();
  }, [API_BASE_URL]);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">LaserMatch API Test</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">API Status</h2>
          <p className="text-lg">{apiStatus}</p>
          <p className="text-sm text-gray-600 mt-2">API URL: {API_BASE_URL}</p>
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-red-800">{error}</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">LaserMatch Items ({items.length})</h2>
          {items.length > 0 ? (
            <div className="space-y-4">
              {items.map((item, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-lg">{item.title}</h3>
                  <div className="grid grid-cols-2 gap-4 mt-2 text-sm">
                    <div><strong>Brand:</strong> {item.brand}</div>
                    <div><strong>Model:</strong> {item.model}</div>
                    <div><strong>Price:</strong> ${item.price?.toLocaleString()}</div>
                    <div><strong>Condition:</strong> {item.condition}</div>
                    <div><strong>Location:</strong> {item.location}</div>
                    <div><strong>Source:</strong> {item.source}</div>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">{item.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600">No items found</p>
          )}
        </div>
      </div>
    </div>
  );
}
