import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { useEffect } from 'react'

// Layouts
import AuthLayout from './layouts/AuthLayout'
import DashboardLayout from './layouts/DashboardLayout'

// Auth Pages
import LoginPage from './pages/auth/LoginPage'

// Dashboard Pages
import SuperAdminDashboard from './pages/dashboards/SuperAdminDashboard'
import CompanyAdminDashboard from './pages/dashboards/CompanyAdminDashboard'
import EmployeeDashboard from './pages/dashboards/EmployeeDashboard'

// LLM Orchestration Pages
import LLMDashboard from './pages/llm/LLMDashboard'
import ModelManagement from './pages/llm/ModelManagement'
import PromptEngineering from './pages/llm/PromptEngineering'
import TrainingData from './pages/llm/TrainingData'

// Knowledge Ingestion Pages
import KnowledgeDashboard from './pages/knowledge/KnowledgeDashboard'
import DocumentUpload from './pages/knowledge/DocumentUpload'
import KnowledgeBase from './pages/knowledge/KnowledgeBase'
import VectorSearch from './pages/knowledge/VectorSearch'

// Branding & Customization Pages
import BrandingDashboard from './pages/branding/BrandingDashboard'
import ThemeEditor from './pages/branding/ThemeEditor'
import LogoManagement from './pages/branding/LogoManagement'

// Workspace Pages
import WorkspaceDashboard from './pages/workspace/WorkspaceDashboard'
import FileManager from './pages/workspace/FileManager'
import JobHistory from './pages/workspace/JobHistory'
import Collaboration from './pages/workspace/Collaboration'

// Employee Pages
import Workspace from './pages/employee/Workspace'
import HeatMaps from './pages/employee/HeatMaps'

// Viewer Pages
import IFCViewer from './pages/viewer/IFCViewer'
import ModelComparison from './pages/viewer/ModelComparison'

// Analytics Pages
import AnalyticsDashboard from './pages/analytics/AnalyticsDashboard'
import PerformanceMetrics from './pages/analytics/PerformanceMetrics'
import UsageReports from './pages/analytics/UsageReports'

// Super Admin Pages
import SubscriptionControl from './pages/subscriptions/SubscriptionControl'
import UserManagement from './pages/admin/UserManagement'
import CompanyManagement from './pages/admin/CompanyManagement'
import SystemSettings from './pages/admin/SystemSettings'
import SuperAdminHeatMaps from './pages/heatmaps/SuperAdminHeatMaps'

// Company Admin Pages
import CredentialVault from './pages/credentials/CredentialVault'
import TeamManagement from './pages/team/TeamManagement'
import CompanyAdminHeatMaps from './pages/heatmaps/CompanyAdminHeatMaps'
import UserGovernance from './pages/company/UserGovernance'

// Protected Route Component
function ProtectedRoute({ children, allowedRoles = [] }) {
  const { isAuthenticated, hasRole } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles.length > 0 && !allowedRoles.some(role => hasRole(role))) {
    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  const { isAuthenticated, user } = useAuthStore()

  useEffect(() => {
    // Initialize app
    console.log('AIBuildX Frontend Initialized')
  }, [])

  const getLandingPage = () => {
    if (user?.role === 'super_admin') return '/superadmin/dashboard'
    if (user?.role === 'company_admin') return '/companyadmin/dashboard'
    if (user?.role === 'employee') return '/employee/dashboard'
    return '/login'
  }

  return (
    <Router>
      <div className="min-h-screen bg-secondary-900 text-secondary-100">
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={isAuthenticated ? <Navigate to={getLandingPage()} replace /> : <AuthLayout />}>
            <Route index element={<LoginPage />} />
          </Route>

          {/* Protected Dashboard Routes */}
          <Route path="/" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
            <Route index element={<Navigate to={getLandingPage()} replace />} />
            <Route path="dashboard" element={<Navigate to={getLandingPage()} replace />} />

            <Route path="superadmin/dashboard" element={<ProtectedRoute allowedRoles={['super_admin']}><SuperAdminDashboard /></ProtectedRoute>} />
            <Route path="superadmin/llm" element={<ProtectedRoute allowedRoles={['super_admin']}><LLMDashboard /></ProtectedRoute>} />
            <Route path="superadmin/llm/models" element={<ProtectedRoute allowedRoles={['super_admin']}><ModelManagement /></ProtectedRoute>} />
            <Route path="superadmin/llm/prompts" element={<ProtectedRoute allowedRoles={['super_admin']}><PromptEngineering /></ProtectedRoute>} />
            <Route path="superadmin/llm/training" element={<ProtectedRoute allowedRoles={['super_admin']}><TrainingData /></ProtectedRoute>} />
            <Route path="superadmin/knowledge" element={<ProtectedRoute allowedRoles={['super_admin']}><KnowledgeDashboard /></ProtectedRoute>} />
            <Route path="superadmin/knowledge/upload" element={<ProtectedRoute allowedRoles={['super_admin']}><DocumentUpload /></ProtectedRoute>} />
            <Route path="superadmin/knowledge/base" element={<ProtectedRoute allowedRoles={['super_admin']}><KnowledgeBase /></ProtectedRoute>} />
            <Route path="superadmin/knowledge/search" element={<ProtectedRoute allowedRoles={['super_admin']}><VectorSearch /></ProtectedRoute>} />
            <Route path="superadmin/subscriptions" element={<ProtectedRoute allowedRoles={['super_admin']}><SubscriptionControl /></ProtectedRoute>} />
            <Route path="superadmin/users" element={<ProtectedRoute allowedRoles={['super_admin']}><UserManagement /></ProtectedRoute>} />
            <Route path="superadmin/companies" element={<ProtectedRoute allowedRoles={['super_admin']}><CompanyManagement /></ProtectedRoute>} />
            <Route path="superadmin/system" element={<ProtectedRoute allowedRoles={['super_admin']}><SystemSettings /></ProtectedRoute>} />
            <Route path="superadmin/heatmaps" element={<ProtectedRoute allowedRoles={['super_admin']}><SuperAdminHeatMaps /></ProtectedRoute>} />

            <Route path="companyadmin/dashboard" element={<ProtectedRoute allowedRoles={['company_admin']}><CompanyAdminDashboard /></ProtectedRoute>} />
            <Route path="companyadmin/branding" element={<ProtectedRoute allowedRoles={['company_admin']}><BrandingDashboard /></ProtectedRoute>} />
            <Route path="companyadmin/branding/theme" element={<ProtectedRoute allowedRoles={['company_admin']}><ThemeEditor /></ProtectedRoute>} />
            <Route path="companyadmin/branding/logo" element={<ProtectedRoute allowedRoles={['company_admin']}><LogoManagement /></ProtectedRoute>} />
            <Route path="companyadmin/credentials" element={<ProtectedRoute allowedRoles={['company_admin']}><CredentialVault /></ProtectedRoute>} />
            <Route path="companyadmin/team" element={<ProtectedRoute allowedRoles={['company_admin']}><TeamManagement /></ProtectedRoute>} />
            <Route path="companyadmin/governance" element={<ProtectedRoute allowedRoles={['company_admin']}><UserGovernance /></ProtectedRoute>} />
            <Route path="companyadmin/heatmaps" element={<ProtectedRoute allowedRoles={['company_admin']}><CompanyAdminHeatMaps /></ProtectedRoute>} />

            <Route path="employee/dashboard" element={<ProtectedRoute allowedRoles={['employee']}><EmployeeDashboard /></ProtectedRoute>} />
            <Route path="employee/workspace" element={<ProtectedRoute allowedRoles={['employee']}><Workspace /></ProtectedRoute>} />
            <Route path="employee/files" element={<ProtectedRoute allowedRoles={['employee']}><FileManager /></ProtectedRoute>} />
            <Route path="employee/jobs" element={<ProtectedRoute allowedRoles={['employee']}><JobHistory /></ProtectedRoute>} />
            <Route path="employee/collaboration" element={<ProtectedRoute allowedRoles={['employee']}><Collaboration /></ProtectedRoute>} />
            <Route path="employee/viewer/:jobId" element={<ProtectedRoute allowedRoles={['employee']}><IFCViewer /></ProtectedRoute>} />
            <Route path="employee/heatmaps" element={<ProtectedRoute allowedRoles={['employee']}><HeatMaps /></ProtectedRoute>} />

            <Route path="viewer" element={<IFCViewer />} />
            <Route path="viewer/:jobId" element={<IFCViewer />} />
            <Route path="viewer/compare" element={<ModelComparison />} />
          </Route>

          {/* Catch all route */}
          <Route path="*" element={<Navigate to={isAuthenticated ? getLandingPage() : '/login'} replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App