import { useEffect, useState } from 'react'
import { useJobStore, JOB_STATUS } from '../../stores/jobStore'
import { useAuthStore } from '../../stores/authStore'
import { motion } from 'framer-motion'
import {
  Users,
  Building,
  TrendingUp,
  Activity,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  BarChart3,
  Zap,
  Target,
  Globe,
  Server,
  AlertTriangle,
  Settings,
  Brain,
  Database
} from 'lucide-react'

function SuperAdminDashboard() {
  const { jobs, fetchJobs } = useJobStore()
  const { user, getAllUsers } = useAuthStore()
  const [systemStats, setSystemStats] = useState({
    totalUsers: 0,
    totalCompanies: 0,
    totalJobs: 0,
    completedJobs: 0,
    processingJobs: 0,
    failedJobs: 0,
    systemUptime: '99.9%',
    avgAccuracy: 0,
    activeUsers: 0,
    serverLoad: '23%',
    alerts: 2
  })

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    const allUsers = getAllUsers()
    const companies = [...new Set(allUsers.filter(u => u.companyId).map(u => u.companyId))]
    const activeUsers = allUsers.filter(u => {
      const lastLogin = new Date(u.lastLogin)
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
      return lastLogin > oneHourAgo
    }).length

    const completedJobs = jobs.filter(job => job.status === JOB_STATUS.COMPLETED)
    const processingJobs = jobs.filter(job => job.status === JOB_STATUS.PROCESSING)
    const failedJobs = jobs.filter(job => job.status === JOB_STATUS.FAILED)

    const totalAccuracy = completedJobs.length > 0
      ? completedJobs.reduce((sum, job) => sum + (job.results?.accuracy || 0), 0) / completedJobs.length
      : 0

    setSystemStats(prev => ({
      ...prev,
      totalUsers: allUsers.length,
      totalCompanies: companies.length,
      totalJobs: jobs.length,
      completedJobs: completedJobs.length,
      processingJobs: processingJobs.length,
      failedJobs: failedJobs.length,
      avgAccuracy: totalAccuracy.toFixed(1),
      activeUsers: activeUsers,
      serverLoad: `${Math.floor(Math.random() * 30 + 20)}%`
    }))
  }, [jobs, getAllUsers])

  const StatCard = ({ title, value, icon: Icon, color, trend, subtitle, isLarge = false }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-secondary-800 border border-secondary-700 rounded-lg p-6 ${isLarge ? 'md:col-span-2' : ''}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-secondary-400 text-sm font-medium">{title}</p>
          <p className={`font-bold text-white mt-1 ${isLarge ? 'text-3xl' : 'text-2xl'}`}>{value}</p>
          {subtitle && <p className="text-secondary-400 text-sm mt-1">{subtitle}</p>}
          {trend && (
            <p className="text-green-400 text-sm mt-1 flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              {trend}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className={`text-white ${isLarge ? 'w-8 h-8' : 'w-6 h-6'}`} />
        </div>
      </div>
    </motion.div>
  )

  const SystemHealthCard = ({ title, status, value, icon: Icon }) => (
    <div className="bg-secondary-800 border border-secondary-700 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${
            status === 'healthy' ? 'bg-green-600/20' :
            status === 'warning' ? 'bg-yellow-600/20' :
            'bg-red-600/20'
          }`}>
            <Icon className={`w-5 h-5 ${
              status === 'healthy' ? 'text-green-400' :
              status === 'warning' ? 'text-yellow-400' :
              'text-red-400'
            }`} />
          </div>
          <div>
            <p className="text-white font-medium">{title}</p>
            <p className="text-secondary-400 text-sm">{value}</p>
          </div>
        </div>
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
          status === 'healthy' ? 'bg-green-500/20 text-green-400' :
          status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
          'bg-red-500/20 text-red-400'
        }`}>
          {status}
        </div>
      </div>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">System Administration</h1>
          <p className="text-secondary-400 mt-1">Monitor and manage the entire AIBuildX platform.</p>
        </div>
        <div className="flex space-x-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-secondary"
          >
            <Server className="w-5 h-5 mr-2" />
            System Status
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary"
          >
            <BarChart3 className="w-5 h-5 mr-2" />
            Analytics
          </motion.button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value={systemStats.totalUsers}
          icon={Users}
          color="bg-blue-600"
          trend="+15% this month"
          subtitle="Across all companies"
        />
        <StatCard
          title="Active Companies"
          value={systemStats.totalCompanies}
          icon={Building}
          color="bg-purple-600"
          trend="+3 this month"
        />
        <StatCard
          title="System Uptime"
          value={systemStats.systemUptime}
          icon={Zap}
          color="bg-green-600"
          subtitle="Last 30 days"
        />
        <StatCard
          title="Active Sessions"
          value={systemStats.activeUsers}
          icon={Globe}
          color="bg-cyan-600"
          subtitle="Real-time users"
        />
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <StatCard
          title="Total Conversions"
          value={systemStats.totalJobs}
          icon={FileText}
          color="bg-indigo-600"
          trend="+22% this week"
          subtitle="All-time conversions"
          isLarge={true}
        />
        <StatCard
          title="Avg Accuracy"
          value={`${systemStats.avgAccuracy}%`}
          icon={Target}
          color="bg-emerald-600"
          subtitle="Quality benchmark"
        />
        <StatCard
          title="System Load"
          value={systemStats.serverLoad}
          icon={Activity}
          color="bg-orange-600"
          subtitle="Current utilization"
        />
      </div>

      {/* System Health & Job Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Server className="w-5 h-5 mr-2 text-primary-400" />
            System Health
          </h2>

          <div className="space-y-3">
            <SystemHealthCard
              title="API Services"
              status="healthy"
              value="All endpoints responding"
              icon={Globe}
            />
            <SystemHealthCard
              title="Database"
              status="healthy"
              value="99.9% uptime"
              icon={Server}
            />
            <SystemHealthCard
              title="AI Models"
              status="warning"
              value="2 models need updates"
              icon={Brain}
            />
            <SystemHealthCard
              title="Storage"
              status="healthy"
              value="78% capacity used"
              icon={Database}
            />
          </div>
        </motion.div>

        {/* Job Status Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-primary-400" />
            Global Job Status
          </h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-white font-medium">Completed</span>
              </div>
              <span className="text-white font-bold text-lg">{systemStats.completedJobs}</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-yellow-500" />
                <span className="text-white font-medium">Processing</span>
              </div>
              <span className="text-white font-bold text-lg">{systemStats.processingJobs}</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <XCircle className="w-5 h-5 text-red-500" />
                <span className="text-white font-medium">Failed</span>
              </div>
              <span className="text-white font-bold text-lg">{systemStats.failedJobs}</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Alerts & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-yellow-400" />
            System Alerts ({systemStats.alerts})
          </h2>

          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-white font-medium">High Memory Usage</p>
                <p className="text-secondary-400 text-sm">Server-3 is using 92% memory. Consider scaling.</p>
                <p className="text-secondary-500 text-xs mt-1">2 hours ago</p>
              </div>
            </div>

            <div className="flex items-start space-x-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <XCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-white font-medium">API Rate Limit Exceeded</p>
                <p className="text-secondary-400 text-sm">Company ACME Corp hit rate limits 5 times today.</p>
                <p className="text-secondary-500 text-xs mt-1">45 minutes ago</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4">Administrative Actions</h2>

          <div className="grid grid-cols-1 gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center space-x-3 p-4 bg-primary-600/20 border border-primary-500/30 rounded-lg hover:bg-primary-600/30 transition-colors text-left"
            >
              <Users className="w-5 h-5 text-primary-400" />
              <div>
                <p className="text-white font-medium">User Management</p>
                <p className="text-secondary-400 text-sm">Manage users and permissions</p>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center space-x-3 p-4 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
            >
              <Building className="w-5 h-5 text-secondary-400" />
              <div>
                <p className="text-white font-medium">Company Administration</p>
                <p className="text-secondary-400 text-sm">Oversee company accounts</p>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center space-x-3 p-4 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
            >
              <BarChart3 className="w-5 h-5 text-secondary-400" />
              <div>
                <p className="text-white font-medium">System Analytics</p>
                <p className="text-secondary-400 text-sm">View detailed platform metrics</p>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center space-x-3 p-4 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
            >
              <Settings className="w-5 h-5 text-secondary-400" />
              <div>
                <p className="text-white font-medium">System Configuration</p>
                <p className="text-secondary-400 text-sm">Configure platform settings</p>
              </div>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default SuperAdminDashboard