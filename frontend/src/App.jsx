import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import CommunitySetup from './pages/CommunitySetup'
import StatusPage from './pages/StatusPage'
import './App.css'

function ProtectedRoute({ children }) {
  // Skip authentication for now - allow access to all routes
  return children
  
  // Original auth code (commented out):
  // const { user, loading } = useAuth()
  // if (loading) {
  //   return <div className="loading">Loading...</div>
  // }
  // if (!user) {
  //   return <Navigate to="/login" replace />
  // }
  // return children
}

function App() {
  return (
    <AuthProvider>
      <div className="app">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/setup/:communityId?"
            element={
              <ProtectedRoute>
                <CommunitySetup />
              </ProtectedRoute>
            }
          />
          <Route
            path="/status/:communityId"
            element={
              <ProtectedRoute>
                <StatusPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </AuthProvider>
  )
}

export default App

