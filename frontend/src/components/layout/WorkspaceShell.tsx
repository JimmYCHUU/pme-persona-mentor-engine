/**
 * WorkspaceShell — root component: opening ritual → NavRail + routed pages.
 */

import { useState, useEffect } from 'react'
import { OpeningRitual } from '../session/OpeningRitual'
import { MasteryCertModal } from '../mastery/MasteryCertModal'
import { ResumeModal } from '../session/ResumeModal'
import { NavRail } from './NavRail'
import { StatusBar } from './StatusBar'
import { SessionPage } from '../../pages/SessionPage'
import { DashboardPage } from '../../pages/DashboardPage'
import { MentorsPage } from '../../pages/MentorsPage'
import { SettingsPage } from '../../pages/SettingsPage'
import { useSessionStore } from '../../store/sessionStore'
import { useMasteryStore } from '../../store/masteryStore'
import { useMastery } from '../../hooks/useMastery'
import { checkHealth } from '../../api/client'

export function WorkspaceShell() {
    const [ritualDone, setRitualDone] = useState(false)
    const [activePath, setActivePath] = useState('/')
    const { mode, snapshot, setProviderStatus } = useSessionStore()
    const { pendingCerts } = useMasteryStore()
    const { markDelivered } = useMastery()
    const [showResume, setShowResume] = useState(true)

    // Poll provider status
    useEffect(() => {
        const poll = async () => {
            try {
                const res = await checkHealth()
                if (res.success && res.data) {
                    const d = res.data as { openrouter_online: boolean; ollama_online: boolean; primary_provider?: string }
                    setProviderStatus({
                        openrouter: d.openrouter_online,
                        ollama: d.ollama_online,
                        primary: d.primary_provider || 'none',
                    })
                }
            } catch { /* silent */ }
        }
        poll()
        const interval = setInterval(poll, 15000)
        return () => clearInterval(interval)
    }, [setProviderStatus])

    if (!ritualDone) {
        return <OpeningRitual onComplete={() => setRitualDone(true)} />
    }

    // Pending cert modal
    if (pendingCerts.length > 0) {
        return (
            <MasteryCertModal
                cert={pendingCerts[0]}
                onClose={() => markDelivered(pendingCerts[0].cert_id)}
            />
        )
    }

    const renderPage = () => {
        switch (activePath) {
            case '/dashboard': return <DashboardPage />
            case '/mentors': return <MentorsPage onNavigateToChat={() => setActivePath('/')} />
            case '/settings': return <SettingsPage />
            default: return <SessionPage />
        }
    }

    return (
        <div
            className={mode === 'friend_mode' ? 'friend-mode' : ''}
            style={{
                display: 'flex', flexDirection: 'column',
                height: '100vh', background: 'var(--bg-base)',
                overflow: 'hidden',
            }}
        >
            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                <NavRail activePath={activePath} onNavigate={setActivePath} />
                <main style={{
                    flex: 1, overflow: 'hidden',
                    display: 'flex', flexDirection: 'column',
                }}>
                    {renderPage()}
                </main>
            </div>
            <StatusBar />

            {/* Resume modal */}
            {snapshot && showResume && activePath === '/' && (
                <ResumeModal
                    snapshot={snapshot}
                    onContinue={() => setShowResume(false)}
                    onStartFresh={() => setShowResume(false)}
                />
            )}
        </div>
    )
}
