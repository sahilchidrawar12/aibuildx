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
  Target
} from 'lucide-react'

function CompanyAdminDashboard() {
  const { jobs, fetchJobs, getCompanyJobs } = useJobStore()
  const { user, getCompanyUsers } = useAuthStore()
  const [stats, setStats] = useState({
    totalJobs: 0,
    completedJobs: 0,
    processingJobs: 0,
    failedJobs: 0,
    totalAccuracy: 0,
    teamMembers: 0,
    activeProjects: 0,
    avgProcessingTime: '42m'
  })

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    const companyJobs = getCompanyJobs()
    const companyUsers = getCompanyUsers(user?.companyId || 'company-1')
    const activeProjects = [...new Set(companyJobs.map(job => job.id))].length // Unique projects

    const completedJobs = companyJobs.filter(job => job.status === JOB_STATUS.COMPLETED)
    const processingJobs = companyJobs.filter(job => job.status === JOB_STATUS.PROCESSING)
    const failedJobs = companyJobs.filter(job => job.status === JOB_STATUS.FAILED)

    const totalAccuracy = completedJobs.length > 0
      ? completedJobs.reduce((sum, job) => sum + (job.results?.accuracy || 0), 0) / completedJobs.length
      : 0

    setStats(prev => ({
      ...prev,
      totalJobs: companyJobs.length,
      completedJobs: completedJobs.length,
      processingJobs: processingJobs.length,
      failedJobs: failedJobs.length,
      totalAccuracy: totalAccuracy.toFixed(1),
      teamMembers: companyUsers.length,
      activeProjects: Math.max(activeProjects, 1) // At least 1 active project
    }))
  }, [jobs, getCompanyJobs, getCompanyUsers, user])

  const recentJobs = getCompanyJobs().slice(0, 6)

  const StatCard = ({ title, value, icon: Icon, color, trend, subtitle }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-secondary-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {subtitle && <p className="text-secondary-400 text-sm mt-1">{subtitle}</p>}
          {trend && (
            <p className="text-green-400 text-sm mt-1 flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              {trend}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </motion.div>
  )

  const JobCard = ({ job }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-secondary-700/50 border border-secondary-600 rounded-lg p-4 hover:bg-secondary-700 transition-colors"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-white font-medium truncate">{job.name}</h3>
          <p className="text-secondary-400 text-sm">{job.fileName}</p>
        </div>
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
          job.status === JOB_STATUS.COMPLETED ? 'bg-green-500/20 text-green-400' :
          job.status === JOB_STATUS.PROCESSING ? 'bg-yellow-500/20 text-yellow-400' :
          job.status === JOB_STATUS.FAILED ? 'bg-red-500/20 text-red-400' :
          'bg-gray-500/20 text-gray-400'
        }`}>
          {job.status}
        </div>
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-secondary-400">
          {new Date(job.createdAt).toLocaleDateString()}
        </span>
        {job.results?.accuracy && (
          <span className="text-green-400 font-medium">
            {job.results.accuracy}% accuracy
          </span>
        )}
      </div>

      {job.status === JOB_STATUS.PROCESSING && (
        <div className="mt-3">
          <div className="flex justify-between text-xs text-secondary-400 mb-1">
            <span>Progress</span>
            <span>{job.progress}%</span>
          </div>
          <div className="w-full bg-secondary-600 rounded-full h-2">
            <div
              className="bg-primary-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${job.progress}%` }}
            />
          </div>
        </div>
      )}
    </motion.div>
  )

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Company Dashboard</h1>
          <p className="text-secondary-400 mt-1">Manage your team's CAD-to-BIM conversions and performance.</p>
        </div>
        <div className="flex space-x-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-secondary"
          >
            <BarChart3 className="w-5 h-5 mr-2" />
            View Reports
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary"
          >
            <Users className="w-5 h-5 mr-2" />
            Manage Team
          </motion.button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Team Members"
          value={stats.teamMembers}
          icon={Users}
          color="bg-blue-600"
          subtitle="Active users"
        />
        <StatCard
          title="Total Conversions"
          value={stats.totalJobs}
          icon={FileText}
          color="bg-purple-600"
          trend="+18% this month"
        />
        <StatCard
          title="Avg Accuracy"
          value={`${stats.totalAccuracy}%`}
          icon={Target}
          color="bg-green-600"
          subtitle="Quality score"
        />
        <StatCard
          title="Active Projects"
          value={stats.activeProjects}
          icon={Building}
          color="bg-orange-600"
          subtitle="In progress"
        />
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Job Status Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-primary-400" />
            Job Status
          </h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-secondary-300">Completed</span>
              </div>
              <span className="text-white font-medium">{stats.completedJobs}</span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-yellow-500" />
                <span className="text-secondary-300">Processing</span>
              </div>
              <span className="text-white font-medium">{stats.processingJobs}</span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <XCircle className="w-4 h-4 text-red-500" />
                <span className="text-secondary-300">Failed</span>
              </div>
              <span className="text-white font-medium">{stats.failedJobs}</span>
            </div>
          </div>
        </motion.div>

        {/* Performance Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-primary-400" />
            Performance
          </h2>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-secondary-400">Avg Processing Time</span>
                <span className="text-white font-medium">{stats.avgProcessingTime}</span>
              </div>
              <div className="w-full bg-secondary-600 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full w-3/4" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-secondary-400">Success Rate</span>
                <span className="text-white font-medium">
                  {stats.totalJobs > 0 ? Math.round((stats.completedJobs / stats.totalJobs) * 100) : 0}%
                </span>
              </div>
              <div className="w-full bg-secondary-600 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${stats.totalJobs > 0 ? (stats.completedJobs / stats.totalJobs) * 100 : 0}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-secondary-400">Quality Score</span>
                <span className="text-white font-medium">{stats.totalAccuracy}%</span>
              </div>
              <div className="w-full bg-secondary-600 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: `${stats.totalAccuracy}%` }}
                />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>

          <div className="space-y-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center space-x-3 p-3 bg-primary-600/20 border border-primary-500/30 rounded-lg hover:bg-primary-600/30 transition-colors text-left"
            >
              <FileText className="w-5 h-5 text-primary-400" />
              <span className="text-white font-medium">New Conversion Job</span>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center space-x-3 p-3 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
            >
              <Users className="w-5 h-5 text-secondary-400" />
              <span className="text-white font-medium">Invite Team Member</span>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center space-x-3 p-3 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
            >
              <BarChart3 className="w-5 h-5 text-secondary-400" />
              <span className="text-white font-medium">Generate Report</span>
            </motion.button>
          </div>
        </motion.div>
      </div>

      {/* Recent Jobs Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">Recent Team Activity</h2>
          <button className="text-primary-400 hover:text-primary-300 text-sm font-medium">
            View All →
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentJobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default CompanyAdminDashboard