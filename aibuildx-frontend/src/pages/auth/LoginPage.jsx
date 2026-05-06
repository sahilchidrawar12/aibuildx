import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { motion } from 'framer-motion'
import { Eye, EyeOff, AlertCircle } from 'lucide-react'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const result = await login(email, password)

      if (result.success && result.user) {
        const landing = result.user.role === 'super_admin'
          ? '/superadmin/dashboard'
          : result.user.role === 'company_admin'
            ? '/companyadmin/dashboard'
            : result.user.role === 'employee'
              ? '/employee/dashboard'
              : '/dashboard'

        navigate(landing)
      } else {
        setError(result.error || 'Login failed')
      }
    } catch (err) {
      setError('An unexpected error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const demoCredentials = [
    { role: 'Super Admin', email: 'superadmin@aibuildx.com', password: 'admin123' },
    { role: 'Company Admin', email: 'admin@company.com', password: 'admin123' },
    { role: 'Employee', email: 'employee@company.com', password: 'employee123' }
  ]

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">Welcome Back</h2>
        <p className="text-secondary-400">Sign in to your AIBuildX account</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-secondary-300 mb-2">
            Email Address
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input w-full"
            placeholder="Enter your email"
            required
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-secondary-300 mb-2">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input w-full pr-10"
              placeholder="Enter your password"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-300"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center space-x-2 text-danger text-sm bg-danger/10 border border-danger/20 rounded-lg p-3"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Signing In...</span>
            </div>
          ) : (
            'Sign In'
          )}
        </button>
      </form>

      {/* Demo Credentials */}
      <div className="border-t border-secondary-700 pt-6">
        <h3 className="text-sm font-medium text-secondary-300 mb-3">Demo Accounts</h3>
        <div className="space-y-2">
          {demoCredentials.map((cred, index) => (
            <button
              key={index}
              onClick={() => {
                setEmail(cred.email)
                setPassword(cred.password)
              }}
              className="w-full text-left p-3 rounded-lg bg-secondary-700/50 hover:bg-secondary-700 transition-colors"
            >
              <div className="text-sm font-medium text-white">{cred.role}</div>
              <div className="text-xs text-secondary-400">{cred.email}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default LoginPage