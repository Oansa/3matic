import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import axios from 'axios'
import './Dashboard.css'

function Dashboard() {
  const navigate = useNavigate()
  // Skip auth for now
  const user = { email: 'test@example.com', name: 'Test User' }
  const logout = () => {
    window.location.href = '/login'
  }
  const [communities, setCommunities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCommunities()
  }, [])

  const fetchCommunities = async () => {
    try {
      // Skip auth token for now
      const response = await axios.get('/api/communities')
      setCommunities(response.data)
    } catch (error) {
      console.error('Failed to fetch communities:', error)
      // Set empty array on error for testing
      setCommunities([])
    } finally {
      setLoading(false)
    }
  }

  const [showNewCommunityModal, setShowNewCommunityModal] = useState(false)
  const [newCommunityName, setNewCommunityName] = useState('')
  const [newCommunityDescription, setNewCommunityDescription] = useState('')

  const handleNewCommunity = () => {
    setShowNewCommunityModal(true)
  }

  const handleCreateCommunity = async () => {
    if (!newCommunityName.trim()) {
      alert('Please enter a community name')
      return
    }

    try {
      const response = await axios.post('/api/communities/create', {
        name: newCommunityName.trim(),
        purpose: newCommunityDescription.trim() || 'General community'
      })
      
      // Add the new community to the list
      setCommunities(prev => [...prev, response.data])
      
      // Reset form and close modal
      setNewCommunityName('')
      setNewCommunityDescription('')
      setShowNewCommunityModal(false)
      
      // Navigate to setup page for the new community
      navigate(`/setup/${response.data._id}`)
    } catch (error) {
      console.error('Failed to create community:', error)
      alert('Failed to create community: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleManageCommunity = (communityId) => {
    navigate(`/setup/${communityId}`)
  }

  const handlePostNow = async (communityId) => {
    try {
      await axios.post(`/api/communities/${communityId}/post-now`)
      alert('Post sent successfully!')
    } catch (error) {
      console.error('Failed to post:', error)
      alert('Failed to send post: ' + (error.response?.data?.detail || error.message))
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>PowerHause</h1>
          <div className="header-actions">
            <span className="user-name">{user?.email || user?.name}</span>
            <button className="logout-btn" onClick={logout}>Logout</button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="section-header">
            <h2>Community Management</h2>
            <button className="btn-primary" onClick={handleNewCommunity}>
              + New Community
            </button>
          </div>

          {communities.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <h3>No communities connected</h3>
              <p>Get started by connecting your first community</p>
              <button className="btn-primary" onClick={handleNewCommunity}>
                Connect Community
              </button>
            </div>
          ) : (
            <div className="communities-grid">
              {communities.map((community) => (
                <div key={community._id} className="community-card">
                  <div className="community-header">
                    <div className="platform-badge">Telegram</div>
                    <div className={`status-badge ${community.status}`}>
                      {community.status}
                    </div>
                  </div>
                  <h3>{community.name || 'Telegram Community'}</h3>
                  <p className="community-description">
                    {community.purpose || 'No description'}
                  </p>
                  <div className="community-stats">
                    <div className="stat">
                      <span className="stat-label">Rules</span>
                      <span className="stat-value">{community.rules?.length || 0}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Documents</span>
                      <span className="stat-value">{community.documents?.length || 0}</span>
                    </div>
                  </div>
                  <div className="community-actions">
                    <button
                      className="btn-secondary"
                      onClick={() => handleManageCommunity(community._id)}
                    >
                      Manage
                    </button>
                    {community.status === 'active' && (
                      <button
                        className="btn-primary"
                        onClick={() => handlePostNow(community._id)}
                      >
                        Post Now
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* New Community Modal */}
      {showNewCommunityModal && (
        <div className="modal-overlay" onClick={() => setShowNewCommunityModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Community</h3>
              <button className="modal-close" onClick={() => setShowNewCommunityModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Community Name</label>
                <input
                  type="text"
                  value={newCommunityName}
                  onChange={(e) => setNewCommunityName(e.target.value)}
                  placeholder="Enter community name"
                  maxLength={100}
                />
              </div>
              <div className="form-group">
                <label>Description (Optional)</label>
                <textarea
                  value={newCommunityDescription}
                  onChange={(e) => setNewCommunityDescription(e.target.value)}
                  placeholder="Describe your community..."
                  rows={3}
                  maxLength={500}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowNewCommunityModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleCreateCommunity}>
                Create Community
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard

