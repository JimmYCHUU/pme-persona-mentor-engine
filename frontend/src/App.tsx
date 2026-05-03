/**
 * App — root React component, wraps WorkspaceShell.
 */

import { useEffect } from 'react'
import './styles/globals.css'
import { WorkspaceShell } from './components/layout/WorkspaceShell'
import { useSessionStore } from './store/sessionStore'
import { useAutoSave } from './hooks/useAutoSave'

function App() {
  const { mode } = useSessionStore()

  // Toggle friend-mode class on body for CSS variable override
  useEffect(() => {
    if (mode === 'friend_mode') {
      document.body.classList.add('friend-mode')
    } else {
      document.body.classList.remove('friend-mode')
    }
  }, [mode])

  // Enable auto-save
  useAutoSave()

  return <WorkspaceShell />
}

export default App
