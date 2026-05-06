import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { Toaster } from 'react-hot-toast'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
    <Toaster
      position="top-right"
      toastOptions={{
        style: {
          background: '#0f1629',
          color: '#e2e8f0',
          border: '1px solid rgba(0,212,255,0.3)'
        }
      }}
    />
  </React.StrictMode>,
)