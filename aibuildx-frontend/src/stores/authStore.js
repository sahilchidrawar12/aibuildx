import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  COMPANY_ADMIN: 'company_admin',
  EMPLOYEE: 'employee'
}

export const PERMISSIONS = {
  // Super Admin permissions
  MANAGE_COMPANIES: 'manage_companies',
  MANAGE_USERS: 'manage_users',
  VIEW_ALL_DATA: 'view_all_data',
  SYSTEM_CONFIG: 'system_config',

  // Company Admin permissions
  MANAGE_EMPLOYEES: 'manage_employees',
  VIEW_COMPANY_DATA: 'view_company_data',
  UPLOAD_FILES: 'upload_files',
  RUN_JOBS: 'run_jobs',

  // Employee permissions
  VIEW_OWN_DATA: 'view_own_data',
  UPLOAD_PERSONAL_FILES: 'upload_personal_files',
  RUN_PERSONAL_JOBS: 'run_personal_jobs'
}

const mockUsers = [
  {
    id: '1',
    email: 'superadmin@aibuildx.com',
    password: 'admin123',
    name: 'Super Admin',
    role: ROLES.SUPER_ADMIN,
    companyId: null,
    avatar: null,
    lastLogin: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000), // Random last login within last week
    permissions: [
      PERMISSIONS.MANAGE_COMPANIES,
      PERMISSIONS.MANAGE_USERS,
      PERMISSIONS.VIEW_ALL_DATA,
      PERMISSIONS.SYSTEM_CONFIG
    ]
  },
  {
    id: '2',
    email: 'admin@company.com',
    password: 'admin123',
    name: 'Company Admin',
    role: ROLES.COMPANY_ADMIN,
    companyId: 'company-1',
    avatar: null,
    lastLogin: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000), // Random last login within last day
    permissions: [
      PERMISSIONS.MANAGE_EMPLOYEES,
      PERMISSIONS.VIEW_COMPANY_DATA,
      PERMISSIONS.UPLOAD_FILES,
      PERMISSIONS.RUN_JOBS
    ]
  },
  {
    id: '3',
    email: 'employee@company.com',
    password: 'employee123',
    name: 'John Employee',
    role: ROLES.EMPLOYEE,
    companyId: 'company-1',
    avatar: null,
    lastLogin: new Date(Date.now() - Math.random() * 2 * 60 * 60 * 1000), // Random last login within last 2 hours
    permissions: [
      PERMISSIONS.VIEW_OWN_DATA,
      PERMISSIONS.UPLOAD_PERSONAL_FILES,
      PERMISSIONS.RUN_PERSONAL_JOBS
    ]
  },
  // Additional dynamic users
  {
    id: '4',
    email: 'sarah.engineer@company.com',
    password: 'engineer123',
    name: 'Sarah Engineer',
    role: ROLES.EMPLOYEE,
    companyId: 'company-1',
    avatar: null,
    lastLogin: new Date(Date.now() - Math.random() * 3 * 60 * 60 * 1000),
    permissions: [
      PERMISSIONS.VIEW_OWN_DATA,
      PERMISSIONS.UPLOAD_PERSONAL_FILES,
      PERMISSIONS.RUN_PERSONAL_JOBS
    ]
  },
  {
    id: '5',
    email: 'mike.architect@company.com',
    password: 'architect123',
    name: 'Mike Architect',
    role: ROLES.EMPLOYEE,
    companyId: 'company-1',
    avatar: null,
    lastLogin: new Date(Date.now() - Math.random() * 6 * 60 * 60 * 1000),
    permissions: [
      PERMISSIONS.VIEW_OWN_DATA,
      PERMISSIONS.UPLOAD_PERSONAL_FILES,
      PERMISSIONS.RUN_PERSONAL_JOBS
    ]
  }
]

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      brandName: 'AIBuildX',
      whiteLabelEnabled: false,

      setBrandName: (brandName) => set({ brandName }),
      setWhiteLabelEnabled: (whiteLabelEnabled) => set({ whiteLabelEnabled }),

      login: async (email, password) => {
        set({ isLoading: true })

        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000))

        const user = mockUsers.find(u => u.email === email && u.password === password)

        if (user) {
          const { password: _, ...userWithoutPassword } = user
          set({
            user: userWithoutPassword,
            isAuthenticated: true,
            isLoading: false
          })
          return { success: true, user: userWithoutPassword }
        } else {
          set({ isLoading: false })
          return { success: false, error: 'Invalid credentials' }
        }
      },

      logout: () => {
        set({
          user: null,
          isAuthenticated: false
        })
      },

      // Get all users (for admin purposes)
      getAllUsers: () => {
        return mockUsers.map(u => {
          const { password, ...userWithoutPassword } = u
          return userWithoutPassword
        })
      },

      // Get users by company
      getCompanyUsers: (companyId) => {
        return mockUsers.filter(u => u.companyId === companyId).map(u => {
          const { password, ...userWithoutPassword } = u
          return userWithoutPassword
        })
      },

      hasPermission: (permission) => {
        const { user } = get()
        return user?.permissions?.includes(permission) || false
      },

      hasRole: (role) => {
        const { user } = get()
        return user?.role === role
      },

      isSuperAdmin: () => get().hasRole(ROLES.SUPER_ADMIN),
      isCompanyAdmin: () => get().hasRole(ROLES.COMPANY_ADMIN),
      isEmployee: () => get().hasRole(ROLES.EMPLOYEE)
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        brandName: state.brandName,
        whiteLabelEnabled: state.whiteLabelEnabled
      })
    }
  )
)