import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useJobStore, JOB_STATUS } from '../../stores/jobStore'
import { motion } from 'framer-motion'
import {
  Upload,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  TrendingUp,
  Activity,
  Zap
} from 'lucide-react'

function EmployeeDashboard() {
  const navigate = useNavigate()
  const { jobs, fetchJobs, getUserJobs } = useJobStore()
  const [stats, setStats] = useState({
    totalJobs: 0,
    completedJobs: 0,
    processingJobs: 0,
    failedJobs: 0,
    totalAccuracy: 0
  })

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    const userJobs = getUserJobs()
    const completedJobs = userJobs.filter(job => job.status === JOB_STATUS.COMPLETED)
    const processingJobs = userJobs.filter(job => job.status === JOB_STATUS.PROCESSING)
    const failedJobs = userJobs.filter(job => job.status === JOB_STATUS.FAILED)

    const totalAccuracy = completedJobs.length > 0
      ? completedJobs.reduce((sum, job) => sum + (job.results?.accuracy || 0), 0) / completedJobs.length
      : 0

    setStats({
      totalJobs: userJobs.length,
      completedJobs: completedJobs.length,
      processingJobs: processingJobs.length,
      failedJobs: failedJobs.length,
      totalAccuracy: totalAccuracy.toFixed(1)
    })
  }, [jobs, getUserJobs])

  const recentJobs = getUserJobs().slice(0, 5)

  const StatCard = ({ title, value, icon: Icon, color, trend }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-secondary-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
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

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-secondary-400 mt-1">Welcome back! Here's your conversion overview.</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/employee/workspace')}
          className="btn-primary flex items-center space-x-2"
        >
          <Upload className="w-5 h-5" />
          <span>Upload New File</span>
        </motion.button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Jobs"
          value={stats.totalJobs}
          icon={FileText}
          color="bg-blue-600"
        />
        <StatCard
          title="Completed"
          value={stats.completedJobs}
          icon={CheckCircle}
          color="bg-green-600"
          trend="+12% this month"
        />
        <StatCard
          title="Processing"
          value={stats.processingJobs}
          icon={Clock}
          color="bg-yellow-600"
        />
        <StatCard
          title="Avg Accuracy"
          value={`${stats.totalAccuracy}%`}
          icon={Zap}
          color="bg-purple-600"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Jobs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-primary-400" />
            Recent Jobs
          </h2>

          <div className="space-y-4">
            {recentJobs.length > 0 ? (
              recentJobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 bg-secondary-700/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      job.status === JOB_STATUS.COMPLETED ? 'bg-green-500' :
                      job.status === JOB_STATUS.PROCESSING ? 'bg-yellow-500' :
                      job.status === JOB_STATUS.FAILED ? 'bg-red-500' : 'bg-gray-500'
                    }`} />
                    <div>
                      <p className="text-white font-medium truncate max-w-xs">{job.name}</p>
                      <p className="text-secondary-400 text-sm">{job.fileName}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-secondary-300 text-sm capitalize">{job.status}</p>
                    {job.results?.accuracy && (
                      <p className="text-green-400 text-sm">{job.results.accuracy}% accuracy</p>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
                <p className="text-secondary-400">No jobs yet. Upload your first CAD file to get started!</p>
              </div>
            )}
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

          <div className="grid grid-cols-1 gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate('/employee/workspace')}
              className="flex items-center space-x-3 p-4 bg-primary-600/20 border border-primary-500/30 rounded-lg hover:bg-primary-600/30 transition-colors text-left"
            >
              <Upload className="w-5 h-5 text-primary-400" />
              <div>
                <p className="text-white font-medium">Upload CAD File</p>
                <p className="text-secondary-400 text-sm">Convert DWG/DXF to BIM</p>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate('/employee/jobs')}
              className="flex items-center space-x-3 p-4 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
            >
              <FileText className="w-5 h-5 text-secondary-400" />
              <div>
                <p className="text-white font-medium">View Job History</p>
                <p className="text-secondary-400 text-sm">Check previous conversions</p>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate('/employee/workspace')}
              className="flex items-center space-x-3 p-4 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
            >
              <Activity className="w-5 h-5 text-secondary-400" />
              <div>
                <p className="text-white font-medium">Browse Templates</p>
                <p className="text-secondary-400 text-sm">Use pre-built configurations</p>
              </div>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default EmployeeDashboard