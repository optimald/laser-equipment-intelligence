'use client'

import { useState } from 'react'
import { PlusIcon, PencilIcon, TrashIcon, UserIcon } from '@heroicons/react/24/outline'

interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'manager' | 'rep'
  active: boolean
  createdAt: string
}

export default function UsersTab() {
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
  const [isAddingUser, setIsAddingUser] = useState(false)
  const [editingUser, setEditingUser] = useState<string | null>(null)
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'rep' as 'admin' | 'manager' | 'rep'
  })

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

  const activeUsers = users.filter(user => user.active)
  const adminUsers = users.filter(user => user.role === 'admin' && user.active)
  const managerUsers = users.filter(user => user.role === 'manager' && user.active)
  const repUsers = users.filter(user => user.role === 'rep' && user.active)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
        <h2 className="text-2xl font-bold text-white">User Management</h2>
        <p className="text-gray-400">Manage team members and their roles in the procurement system</p>
        </div>
        <button
          onClick={() => setIsAddingUser(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add User
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-900 p-4 rounded-lg border border-gray-800">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <UserIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <div className="text-2xl font-bold text-white">{activeUsers.length}</div>
              <div className="text-sm text-gray-400">Active Users</div>
            </div>
          </div>
        </div>
        <div className="bg-gray-900 p-4 rounded-lg border border-gray-800">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <UserIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-3">
              <div className="text-2xl font-bold text-white">{adminUsers.length}</div>
              <div className="text-sm text-gray-400">Admins</div>
            </div>
          </div>
        </div>
        <div className="bg-gray-900 p-4 rounded-lg border border-gray-800">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <UserIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <div className="text-2xl font-bold text-white">{managerUsers.length}</div>
              <div className="text-sm text-gray-400">Managers</div>
            </div>
          </div>
        </div>
        <div className="bg-gray-900 p-4 rounded-lg border border-gray-800">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <UserIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-3">
              <div className="text-2xl font-bold text-white">{repUsers.length}</div>
              <div className="text-sm text-gray-400">Reps</div>
            </div>
          </div>
        </div>
      </div>

      {/* Add User Form */}
      {isAddingUser && (
        <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
          <h3 className="text-lg font-medium text-white mb-4">Add New User</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <input
              type="text"
              placeholder="Full name *"
              value={newUser.name}
              onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
            />
            <input
              type="email"
              placeholder="Email address *"
              value={newUser.email}
              onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
            />
            <select
              value={newUser.role}
              onChange={(e) => setNewUser(prev => ({ ...prev, role: e.target.value as 'admin' | 'manager' | 'rep' }))}
              className="px-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md text-sm focus:border-gray-500 focus:outline-none"
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
              className="px-4 py-2 text-sm text-gray-400 hover:text-gray-700"
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
      <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800">
          <h3 className="text-lg font-medium text-white">Team Members</h3>
          <p className="text-sm text-gray-400">Manage user accounts and permissions</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-gray-900 divide-y divide-gray-700">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                          <UserIcon className="h-6 w-6 text-gray-400" />
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-white">{user.name}</div>
                        <div className="text-sm text-gray-400">{user.email}</div>
                      </div>
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
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                    {new Date(user.createdAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => setEditingUser(user.id)}
                        className="text-blue-600 hover:text-blue-700 p-1"
                        title="Edit user"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => updateUser(user.id, { active: !user.active })}
                        className={`text-xs px-3 py-1 rounded ${
                          user.active 
                            ? 'text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100' 
                            : 'text-green-600 hover:text-green-700 bg-green-50 hover:bg-green-100'
                        }`}
                      >
                        {user.active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        onClick={() => deleteUser(user.id)}
                        className="text-red-600 hover:text-red-700 p-1"
                        title="Delete user"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {users.length === 0 && (
          <div className="text-center py-12">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-white">No users</h3>
            <p className="mt-1 text-sm text-gray-400">Get started by adding your first team member.</p>
            <div className="mt-6">
              <button
                onClick={() => setIsAddingUser(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add User
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
