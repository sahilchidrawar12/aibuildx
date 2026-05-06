# AIBuildX Frontend

A production-grade React SaaS application for AI-powered CAD-to-BIM conversion with an industrial sci-fi command center aesthetic.

## Features

- **Role-based Authentication**: Super Admin, Company Admin, and Employee roles with protected routes
- **Industrial Sci-Fi Design**: Dark theme with cyan accents, glowing effects, and precision-focused UI
- **Dashboard System**: Comprehensive dashboards for each role with real-time metrics
- **LLM Orchestration**: AI model management and monitoring interface
- **Knowledge Base**: Document upload and vector search capabilities
- **3D IFC Viewer**: Three.js-powered model visualization (placeholder implemented)
- **Branding System**: Customizable themes and brand assets (Super Admin only)
- **API Integration**: Axios-based communication with Flask backend

## Tech Stack

- **React 18** with Vite for fast development
- **Tailwind CSS** for styling with custom industrial theme
- **React Router v6** for client-side routing
- **Zustand** for global state management
- **Framer Motion** for animations
- **Three.js + React Three Fiber** for 3D visualization
- **Recharts** for data visualization
- **Axios** for API calls

## Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/          # Reusable UI components
├── layouts/            # Layout components (Auth, Dashboard)
├── pages/              # Page components organized by feature
│   ├── auth/           # Authentication pages
│   ├── dashboards/     # Role-specific dashboards
│   ├── llm/            # LLM orchestration pages
│   ├── knowledge/      # Knowledge base pages
│   ├── branding/       # Branding customization pages
│   ├── viewer/         # IFC viewer pages
│   └── ...
├── stores/             # Zustand state stores
├── lib/                # Utility functions
└── main.jsx           # Application entry point
```

## Authentication

The app includes mock authentication with three user roles:

- **Super Admin** (`superadmin@aibuildx.com` / `admin123`)
  - Full system access, branding management, user administration
- **Company Admin** (`admin@company.com` / `admin123`)
  - Team management, analytics, job oversight
- **Employee** (`employee@company.com` / `employee123`)
  - Personal dashboard, file uploads, job monitoring

## API Integration

The frontend is configured to proxy API calls to `http://localhost:5000` (Flask backend). Key endpoints include:

- `/api/jobs` - Job management
- `/api/users` - User management
- `/api/models` - AI model operations
- `/api/documents` - Knowledge base operations

## Design System

- **Colors**: Primary cyan (#00ffff), secondary dark (#1e293b), accent cyan (#00ffff)
- **Typography**: JetBrains Mono for monospace, Inter for sans-serif
- **Effects**: Glow effects, subtle animations, industrial precision aesthetic
- **Components**: Custom button styles, form inputs, card layouts

## Development

- **Linting**: ESLint with React rules
- **Styling**: Tailwind CSS with custom configuration
- **State Management**: Zustand stores for auth and job management
- **Routing**: Protected routes with role-based access control

## Browser Support

- Modern browsers with ES6+ support
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

## Contributing

1. Follow the existing code structure and naming conventions
2. Use TypeScript for new components when possible
3. Maintain the industrial sci-fi aesthetic
4. Test authentication flows and role-based access
5. Ensure responsive design across devices