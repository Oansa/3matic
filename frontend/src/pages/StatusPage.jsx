import { useState, useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import axios from 'axios'
import './StatusPage.css'

function StatusPage() {
  const navigate = useNavigate()
  const { communityId } = useParams()
  const location = useLocation()
  const { user } = useAuth()
  const [community, setCommunity] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deploymentStatus, setDeploymentStatus] = useState(null)

  // Get deployment status from navigation state
  useEffect(() => {
    if (location.state?.deploymentStatus) {
      setDeploymentStatus(location.state.deploymentStatus)
    }
  }, [location.state])

  useEffect(() => {
    if (communityId) {
      fetchCommunity()
    }
  }, [communityId])

  const fetchCommunity = async () => {
    try {
      const response = await axios.get(`/api/communities/${communityId}`)
      setCommunity(response.data)
    } catch (error) {
      console.error('Failed to fetch community:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePostNow = async () => {
    try {
      await axios.post(`/api/communities/${communityId}/post-now`)
      alert('Post sent successfully!')
    } catch (error) {
      console.error('Failed to post:', error)
      alert('Failed to send post: ' + (error.response?.data?.detail || error.message))
    }
  }

  if (loading) {
    return <div className="status-page">
      <div className="loading">Loading community status...</div>
    </div>
  }

  if (!community) {
    return <div className="status-page">
      <div className="error">Community not found</div>
      <button className="btn-primary" onClick={() => navigate('/dashboard')}>
        Back to Dashboard
      </button>
    </div>
  }

  return (
    <div className="status-page">
      <header className="status-header">
        <button className="back-button" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
      </header>

      <main className="status-main">
        <div className="status-content">
          <div className="status-card">
            <div className="status-icon">
              {deploymentStatus?.status === 'deployed' ? '✅' : '⚠️'}
            </div>
            <h1>Community Deployed Successfully!</h1>
            <p className="status-message">
              {deploymentStatus?.message || 'Your Telegram community manager is now active.'}
            </p>
          </div>

          <div className="community-info">
            <h2>Community Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Name</span>
                <span className="info-value">{community.name || 'Telegram Community'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Status</span>
                <span className={`info-value status-${community.status}`}>
                  {community.status}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Bot Token</span>
                <span className="info-value">
                  {community.telegram_token ? 
                    `${community.telegram_token.substring(0, 10)}...` : 
                    'Not configured'
                  }
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Chat ID</span>
                <span className="info-value">{community.telegram_chat_id || 'Not configured'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Purpose</span>
                <span className="info-value">{community.purpose || 'Not specified'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Posting Frequency</span>
                <span className="info-value">{community.postingFrequency || 'Not set'}</span>
              </div>
            </div>
          </div>

          <div className="actions-section">
            <h2>Actions</h2>
            <div className="action-buttons">
              <button 
                className="btn-primary"
                onClick={handlePostNow}
                disabled={community.status !== 'active'}
              >
                📤 Post Something Now
              </button>
              <button 
                className="btn-secondary"
                onClick={() => navigate(`/setup/${communityId}`)}
              >
                ⚙️ Manage Settings
              </button>
            </div>
            <p className="action-note">
              The bot will automatically post according to your frequency settings. 
              Use "Post Now" to send an immediate message.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default StatusPage