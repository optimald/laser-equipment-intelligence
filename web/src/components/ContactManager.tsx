'use client'

import { useState, useEffect } from 'react'
import { PlusIcon, PencilIcon, TrashIcon, PhoneIcon, EnvelopeIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline'

interface Contact {
  id: string
  name: string
  company: string
  email: string
  phone: string
  website?: string
  notes?: string
  tags: string[]
  createdAt: string
  updatedAt: string
}

export default function ContactManager() {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [isAddingContact, setIsAddingContact] = useState(false)
  const [editingContact, setEditingContact] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [newContact, setNewContact] = useState({
    name: '',
    company: '',
    email: '',
    phone: '',
    website: '',
    notes: '',
    tags: [] as string[]
  })

  // Sample data for development
  useEffect(() => {
    const sampleContacts: Contact[] = [
      {
        id: '1',
        name: 'John Smith',
        company: 'MedTech Solutions',
        email: 'john.smith@medtech.com',
        phone: '+1 (555) 123-4567',
        website: 'https://medtech.com',
        notes: 'Primary contact for laser equipment sales',
        tags: ['laser-equipment', 'sales', 'preferred'],
        createdAt: '2024-01-15T10:00:00Z',
        updatedAt: '2024-01-15T10:00:00Z'
      },
      {
        id: '2',
        name: 'Sarah Johnson',
        company: 'Laser Dynamics Inc',
        email: 'sarah@laserdynamics.com',
        phone: '+1 (555) 987-6543',
        website: 'https://laserdynamics.com',
        notes: 'Specializes in Aerolase equipment',
        tags: ['aerolase', 'equipment', 'specialist'],
        createdAt: '2024-01-16T14:30:00Z',
        updatedAt: '2024-01-16T14:30:00Z'
      }
    ]
    setContacts(sampleContacts)
  }, [])

  const addContact = () => {
    if (!newContact.name.trim() || !newContact.email.trim()) return

    const contact: Contact = {
      id: Date.now().toString(),
      name: newContact.name.trim(),
      company: newContact.company.trim(),
      email: newContact.email.trim(),
      phone: newContact.phone.trim(),
      website: newContact.website.trim() || undefined,
      notes: newContact.notes.trim() || undefined,
      tags: newContact.tags,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    setContacts(prev => [contact, ...prev])
    resetForm()
  }

  const updateContact = (contactId: string, updates: Partial<Contact>) => {
    setContacts(prev => prev.map(contact => 
      contact.id === contactId 
        ? { ...contact, ...updates, updatedAt: new Date().toISOString() }
        : contact
    ))
  }

  const deleteContact = (contactId: string) => {
    if (confirm('Are you sure you want to delete this contact?')) {
      setContacts(prev => prev.filter(contact => contact.id !== contactId))
    }
  }

  const resetForm = () => {
    setNewContact({
      name: '',
      company: '',
      email: '',
      phone: '',
      website: '',
      notes: '',
      tags: []
    })
    setIsAddingContact(false)
    setEditingContact(null)
  }

  const filteredContacts = contacts.filter(contact => {
    const matchesSearch = searchTerm === '' || 
      contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.email.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesTags = selectedTags.length === 0 || 
      selectedTags.some(tag => contact.tags.includes(tag))
    
    return matchesSearch && matchesTags
  })

  const allTags = Array.from(new Set(contacts.flatMap(contact => contact.tags)))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Contact Manager</h2>
          <p className="text-gray-400">Manage your supplier and vendor contacts</p>
        </div>
        <button
          onClick={() => setIsAddingContact(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Contact
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-gray-900 p-4 rounded-lg border border-gray-800" style={{backgroundColor: '#111827'}}>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search contacts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
              style={{backgroundColor: '#1f2937', color: 'white', borderColor: '#4b5563'}}
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {allTags.map(tag => (
              <button
                key={tag}
                onClick={() => {
                  setSelectedTags(prev => 
                    prev.includes(tag) 
                      ? prev.filter(t => t !== tag)
                      : [...prev, tag]
                  )
                }}
                className={`px-3 py-1 text-xs rounded-full border ${
                  selectedTags.includes(tag)
                    ? 'bg-blue-700 text-blue-200 border-blue-600'
                    : 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Add Contact Form */}
      {isAddingContact && (
        <div className="bg-gray-900 p-6 rounded-lg border border-gray-800" style={{backgroundColor: '#111827', borderColor: '#374151'}}>
          <h3 className="text-lg font-medium text-white mb-4">Add New Contact</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <input
              type="text"
              placeholder="Full name *"
              value={newContact.name}
              onChange={(e) => setNewContact(prev => ({ ...prev, name: e.target.value }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
            />
            <input
              type="text"
              placeholder="Company"
              value={newContact.company}
              onChange={(e) => setNewContact(prev => ({ ...prev, company: e.target.value }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
            />
            <input
              type="email"
              placeholder="Email address *"
              value={newContact.email}
              onChange={(e) => setNewContact(prev => ({ ...prev, email: e.target.value }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
            />
            <input
              type="tel"
              placeholder="Phone number"
              value={newContact.phone}
              onChange={(e) => setNewContact(prev => ({ ...prev, phone: e.target.value }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
            />
            <input
              type="url"
              placeholder="Website"
              value={newContact.website}
              onChange={(e) => setNewContact(prev => ({ ...prev, website: e.target.value }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
            />
            <input
              type="text"
              placeholder="Tags (comma separated)"
              onChange={(e) => setNewContact(prev => ({ 
                ...prev, 
                tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
              }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
            />
          </div>
          <textarea
            placeholder="Notes"
            value={newContact.notes}
            onChange={(e) => setNewContact(prev => ({ ...prev, notes: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm h-20 resize-none mb-4 focus:border-gray-500 focus:outline-none"
          />
          <div className="flex justify-end space-x-2">
            <button
              onClick={resetForm}
              className="px-4 py-2 text-sm text-gray-400 hover:text-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={addContact}
              disabled={!newContact.name.trim() || !newContact.email.trim()}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed"
            >
              Add Contact
            </button>
          </div>
        </div>
      )}

      {/* Contacts List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredContacts.map(contact => (
          <div key={contact.id} className="bg-gray-900 p-4 rounded-lg border border-gray-800 hover:border-gray-700 transition-colors" style={{backgroundColor: '#111827', borderColor: '#374151'}}>
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-medium text-white">{contact.name}</h3>
                {contact.company && (
                  <p className="text-sm text-gray-400 flex items-center mt-1">
                    <BuildingOfficeIcon className="h-4 w-4 mr-1" />
                    {contact.company}
                  </p>
                )}
              </div>
              <div className="flex space-x-1">
                <button
                  onClick={() => setEditingContact(contact.id)}
                  className="p-1 text-gray-400 hover:text-gray-300"
                >
                  <PencilIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => deleteContact(contact.id)}
                  className="p-1 text-gray-400 hover:text-red-400"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="space-y-2 mb-3">
              <a
                href={`mailto:${contact.email}`}
                className="flex items-center text-sm text-blue-400 hover:text-blue-300"
              >
                <EnvelopeIcon className="h-4 w-4 mr-2" />
                {contact.email}
              </a>
              {contact.phone && (
                <a
                  href={`tel:${contact.phone}`}
                  className="flex items-center text-sm text-blue-400 hover:text-blue-300"
                >
                  <PhoneIcon className="h-4 w-4 mr-2" />
                  {contact.phone}
                </a>
              )}
              {contact.website && (
                <a
                  href={contact.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  Visit Website →
                </a>
              )}
            </div>

            {contact.notes && (
              <p className="text-sm text-gray-400 mb-3">{contact.notes}</p>
            )}

            {contact.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {contact.tags.map(tag => (
                  <span
                    key={tag}
                    className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredContacts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400">
            {searchTerm || selectedTags.length > 0 
              ? 'No contacts match your search criteria.'
              : 'No contacts yet. Click "Add Contact" to get started.'
            }
          </p>
        </div>
      )}
    </div>
  )
}
