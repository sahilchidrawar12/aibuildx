import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  Brain,
  Database,
  Palette,
  FolderOpen,
  Eye,
  BarChart3,
  Settings,
  User,
  LogOut,
  Menu,
  X,
  ChevronDown,
  Bell,
  Search
} from 'lucide-react'

const routeMap = {
  super_admin: [
    { name: 'Dashboard', href: '/superadmin/dashboard', icon: LayoutDashboard },
    { name: 'LLM Orchestration', href: '/superadmin/llm', icon: Brain },
    { name: 'Knowledge Base', href: '/superadmin/knowledge', icon: Database },
    { name: 'Subscriptions', href: '/superadmin/subscriptions', icon: BarChart3 },
    { name: 'Heatmaps', href: '/superadmin/heatmaps', icon: Eye },
    {
      name: 'Admin',
      href: '/superadmin/users',
      icon: Settings,
      children: [
        { name: 'Users', href: '/superadmin/users' },
        { name: 'Companies', href: '/superadmin/companies' },
        { name: 'System', href: '/superadmin/system' }
      ]
    }
  ],
  company_admin: [
    { name: 'Dashboard', href: '/companyadmin/dashboard', icon: LayoutDashboard },
    { name: 'Branding', href: '/companyadmin/branding', icon: Palette },
    { name: 'Credentials', href: '/companyadmin/credentials', icon: Database },
    { name: 'Team', href: '/companyadmin/team', icon: FolderOpen },
    { name: 'Governance', href: '/companyadmin/governance', icon: User },
    { name: 'Heatmaps', href: '/companyadmin/heatmaps', icon: Eye }
  ],
  employee: [
    { name: 'Dashboard', href: '/employee/dashboard', icon: LayoutDashboard },
    { name: 'Workspace', href: '/employee/workspace', icon: FolderOpen },
    { name: 'Files', href: '/employee/files', icon: Database },
    { name: 'Jobs', href: '/employee/jobs', icon: BarChart3 },
    { name: 'Collaboration', href: '/employee/collaboration', icon: User },
    { name: 'IFC Viewer', href: '/viewer', icon: Eye }
  ]
}

function DashboardLayout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth >= 1024)
  const [isLargeScreen, setIsLargeScreen] = useState(window.innerWidth >= 1024)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(min-width: 1024px)')
    const updateScreen = (event) => {
      const large = event?.matches ?? mediaQuery.matches
      setIsLargeScreen(large)
      if (large) {
        setSidebarOpen(true)
      }
    }

    updateScreen()
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', updateScreen)
    } else {
      mediaQuery.addListener(updateScreen)
    }

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', updateScreen)
      } else {
        mediaQuery.removeListener(updateScreen)
      }
    }
  }, [])

  // Ensure sidebar stays open on large screens
  useEffect(() => {
    if (isLargeScreen) {
      setSidebarOpen(true)
    }
  }, [isLargeScreen])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navigationItems = routeMap[user?.role] || []
  const filteredNavItems = navigationItems

  const isActiveRoute = (href) => location.pathname === href || location.pathname.startsWith(`${href}/`)

  return (
    <div className="min-h-screen bg-secondary-900 overflow-x-hidden lg:flex lg:h-screen">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && !isLargeScreen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <div className="absolute inset-0 bg-secondary-900/80 backdrop-blur-sm" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={isLargeScreen ? {} : { x: sidebarOpen ? 0 : -320 }}
        className="fixed inset-y-0 left-0 z-50 w-80 overflow-y-auto bg-secondary-800 border-r border-secondary-700 lg:static lg:inset-auto lg:h-screen lg:w-80 lg:overflow-y-auto"
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-secondary-700">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-cyan rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AX</span>
              </div>
              <div>
                <h1 className="text-white font-bold text-lg">AIBuildX</h1>
                <p className="text-secondary-400 text-xs">Command Center</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-secondary-400 hover:text-white"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {filteredNavItems.map((item) => (
              <div key={item.name}>
                <button
                  onClick={() => {
                    navigate(item.href)
                    if (!isLargeScreen) {
                      setSidebarOpen(false)
                    }
                  }}
                  className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-all duration-200 ${
                    isActiveRoute(item.href)
                      ? 'bg-primary-600/20 text-primary-300 border-l-2 border-primary-500'
                      : 'text-secondary-300 hover:bg-secondary-700 hover:text-white'
                  }`}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  <span className="font-medium">{item.name}</span>
                  {item.children && (
                    <ChevronDown className="w-4 h-4 ml-auto" />
                  )}
                </button>

                {/* Submenu */}
                {item.children && isActiveRoute(item.href) && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="ml-8 mt-2 space-y-1"
                  >
                    {item.children.map((child) => (
                      <button
                        key={child.name}
                        onClick={() => {
                          navigate(child.href)
                          if (!isLargeScreen) {
                            setSidebarOpen(false)
                          }
                        }}
                        className={`w-full flex items-center px-3 py-2 text-left rounded-md transition-colors ${
                          location.pathname === child.href
                            ? 'bg-primary-500/20 text-primary-300'
                            : 'text-secondary-400 hover:text-secondary-200'
                        }`}
                      >
                        <span className="text-sm">{child.name}</span>
                      </button>
                    ))}
                  </motion.div>
                )}
              </div>
            ))}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-secondary-700">
            <div className="flex items-center space-x-3 p-3 rounded-lg bg-secondary-700/50">
              <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">{user?.name}</p>
                <p className="text-secondary-400 text-sm capitalize">{user?.role?.replace('_', ' ')}</p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="flex-1 min-h-screen overflow-y-auto">
        {/* Top bar */}
        <header className="sticky top-0 z-20 bg-secondary-800 border-b border-secondary-700 px-4 py-3 lg:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-secondary-400 hover:text-white"
              >
                <Menu className="w-6 h-6" />
              </button>

              <div className="hidden md:block">
                <div className="relative">
                  <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400" />
                  <input
                    type="text"
                    placeholder="Search..."
                    className="w-72 h-10 rounded-2xl border border-secondary-700 bg-secondary-900/90 pl-11 pr-4 text-sm text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button className="text-secondary-400 hover:text-white relative">
                <Bell className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-danger rounded-full"></span>
              </button>

              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 text-secondary-300 hover:text-white"
                >
                  <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <ChevronDown className="w-4 h-4" />
                </button>

                <AnimatePresence>
                  {userMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="absolute right-0 mt-2 w-48 bg-secondary-800 border border-secondary-700 rounded-lg shadow-lg py-1 z-50"
                    >
                      <div className="px-4 py-2 border-b border-secondary-700">
                        <p className="text-white font-medium">{user?.name}</p>
                        <p className="text-secondary-400 text-sm">{user?.email}</p>
                      </div>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center px-4 py-2 text-left text-secondary-300 hover:bg-secondary-700 hover:text-white"
                      >
                        <LogOut className="w-4 h-4 mr-2" />
                        Sign Out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="min-h-screen p-4 lg:p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout