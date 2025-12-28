import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import axios from 'axios'
import './CommunitySetup.css'

function CommunitySetup() {
  const navigate = useNavigate()
  const { communityId } = useParams()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    purpose: '',
    rules: [''],
    moderationLevel: 'medium',
    engagementStyle: 'friendly',
    postingFrequency: 'moderate',
    telegramToken: '',
    telegramChatId: ''
  })

  useEffect(() => {
    if (communityId) {
      fetchCommunity()
    }
  }, [communityId])

  const fetchCommunity = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`/api/communities/${communityId}`)
      const community = response.data

      setFormData({
        name: community.name || '',
        purpose: community.purpose || '',
        rules: community.rules && community.rules.length > 0 ? community.rules : [''],
        moderationLevel: community.moderationLevel || 'medium',
        engagementStyle: community.engagementStyle || 'friendly',
        postingFrequency: community.postingFrequency || 'moderate',
        telegramToken: community.telegram_token || '',
        telegramChatId: community.telegram_chat_id || ''
      })
    } catch (error) {
      console.error('Failed to fetch community:', error)
      alert('Failed to load community data')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleRuleChange = (index, value) => {
    const newRules = [...formData.rules]
    newRules[index] = value
    setFormData(prev => ({
      ...prev,
      rules: newRules
    }))
  }

  const addRule = () => {
    setFormData(prev => ({
      ...prev,
      rules: [...prev.rules, '']
    }))
  }

  const removeRule = (index) => {
    if (formData.rules.length > 1) {
      const newRules = formData.rules.filter((_, i) => i !== index)
      setFormData(prev => ({
        ...prev,
        rules: newRules
      }))
    }
  }

  const handleSave = async () => {
    if (!formData.name.trim()) {
      alert('Community name is required')
      return
    }

    setSaving(true)
    try {
      const updateData = {
        name: formData.name.trim(),
        purpose: formData.purpose.trim(),
        rules: formData.rules.filter(rule => rule.trim() !== ''),
        moderationLevel: formData.moderationLevel,
        engagementStyle: formData.engagementStyle,
        postingFrequency: formData.postingFrequency,
        telegram_token: formData.telegramToken.trim(),
        telegram_chat_id: formData.telegramChatId.trim()
      }

      await axios.put(`/api/communities/${communityId}`, updateData)
      alert('Community settings saved successfully!')
    } catch (error) {
      console.error('Failed to save community:', error)
      alert('Failed to save community: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSaving(false)
    }
  }

  const handleDeploy = async () => {
    if (!formData.telegramToken.trim() || !formData.telegramChatId.trim()) {
      alert('Telegram bot token and chat ID are required for deployment')
      return
    }

    setLoading(true)
    try {
      console.log(`Calling deploy API: /api/communities/${communityId}/deploy`)
      const response = await axios.post(`/api/communities/${communityId}/deploy`, {})

      console.log('Deploy response:', response.data)

      if (response.data && response.data.status === 'deployed') {
        console.log('Deployment successful, navigating to status page in 2 seconds...')
        setTimeout(() => {
          navigate(`/status/${communityId}`, {
            state: { deploymentStatus: response.data }
          })
        }, 2000)
      } else {
        console.error('Invalid deployment response:', response.data)
        throw new Error('Deployment response was invalid')
      }
    } catch (error) {
      console.error('Deploy error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      })

      alert('Failed to deploy: ' + (error.response?.data?.detail || error.response?.data?.message || error.message))
    } finally {
      setLoading(false)
    }
  }

  if (loading && !communityId) {
    return <div className="community-setup">
      <div className="loading">Loading...</div>
    </div>
  }

  return (
    <div className="community-setup">
      <header className="setup-header">
        <button className="back-button" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
        <h1>{communityId ? 'Configure Community' : 'Setup Community'}</h1>
      </header>

      <main className="setup-main">
        <div className="setup-form">
          <div className="form-section">
            <h2>Basic Information</h2>
            <div className="form-group">
              <label>Community Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter community name"
                maxLength={100}
              />
            </div>
            <div className="form-group">
              <label>Purpose & Description</label>
              <textarea
                value={formData.purpose}
                onChange={(e) => handleInputChange('purpose', e.target.value)}
                placeholder="Describe what this community is about..."
                rows={3}
                maxLength={500}
              />
            </div>
          </div>

          <div className="form-section">
            <h2>Community Rules</h2>
            {formData.rules.map((rule, index) => (
              <div key={index} className="rule-group">
                <input
                  type="text"
                  value={rule}
                  onChange={(e) => handleRuleChange(index, e.target.value)}
                  placeholder={`Rule ${index + 1}`}
                  maxLength={200}
                />
                {formData.rules.length > 1 && (
                  <button
                    type="button"
                    className="remove-rule-btn"
                    onClick={() => removeRule(index)}
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
            <button type="button" className="add-rule-btn" onClick={addRule}>
              + Add Rule
            </button>
          </div>

          <div className="form-section">
            <h2>AI Configuration</h2>
            <div className="form-row">
              <div className="form-group">
                <label>Moderation Level</label>
                <select
                  value={formData.moderationLevel}
                  onChange={(e) => handleInputChange('moderationLevel', e.target.value)}
                >
                  <option value="low">Low - Relaxed moderation</option>
                  <option value="medium">Medium - Balanced approach</option>
                  <option value="high">High - Strict moderation</option>
                </select>
              </div>
              <div className="form-group">
                <label>Engagement Style</label>
                <select
                  value={formData.engagementStyle}
                  onChange={(e) => handleInputChange('engagementStyle', e.target.value)}
                >
                  <option value="formal">Formal - Professional tone</option>
                  <option value="friendly">Friendly - Casual and approachable</option>
                  <option value="casual">Casual - Very relaxed</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Posting Frequency</label>
              <select
                value={formData.postingFrequency}
                onChange={(e) => handleInputChange('postingFrequency', e.target.value)}
              >
                <option value="low">Low - Once per day</option>
                <option value="moderate">Moderate - Twice per day</option>
                <option value="high">High - Four times per day</option>
              </select>
            </div>
          </div>

          <div className="form-section">
            <h2>Telegram Integration</h2>
            <div className="form-group">
              <label>Bot Token *</label>
              <input
                type="text"
                value={formData.telegramToken}
                onChange={(e) => handleInputChange('telegramToken', e.target.value)}
                placeholder="Enter your Telegram bot token from @BotFather"
              />
            </div>
            <div className="form-group">
              <label>Chat ID *</label>
              <input
                type="text"
                value={formData.telegramChatId}
                onChange={(e) => handleInputChange('telegramChatId', e.target.value)}
                placeholder="Enter the chat ID of your Telegram group"
              />
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={handleDeploy}
              disabled={loading || !formData.telegramToken.trim() || !formData.telegramChatId.trim()}
            >
              {loading ? 'Deploying...' : 'Deploy Community'}
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}

export default CommunitySetup

