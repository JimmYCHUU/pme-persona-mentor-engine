/**
 * PME Workspace Monitor — VS Code Extension
 * Monitors terminal errors, file saves, and idle time.
 * Posts events to http://localhost:8000/workspace/event
 */

import * as vscode from 'vscode'
import axios from 'axios'

const PME_URL = 'http://localhost:8000/workspace/event'

let idleTimer: NodeJS.Timeout | undefined
const IDLE_MS = 300_000 // 5 minutes - matches backend IDLE_TRIGGER_SECONDS

async function postEvent(payload: object): Promise<void> {
    try {
        await axios.post(PME_URL, payload, { timeout: 3000 })
    } catch {
        /* never crash VS Code */
    }
}

function isError(text: string): boolean {
    return /error|exception|traceback|failed|syntaxerror|typeerror/i.test(text)
}

function resetIdleTimer(): void {
    if (idleTimer) clearTimeout(idleTimer)
    idleTimer = setTimeout(() => {
        postEvent({ type: 'idle', duration_seconds: 300 })
    }, IDLE_MS)
}

export function activate(ctx: vscode.ExtensionContext): void {
    // 1. Watch terminal output for errors
    ctx.subscriptions.push(
        vscode.window.onDidWriteTerminalData(e => {
            if (isError(e.data)) {
                postEvent({ type: 'terminal_error', content: e.data.slice(0, 1000) })
            }
        })
    )

    // 2. Watch for file saves
    ctx.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(doc => {
            postEvent({
                type: 'file_save',
                file: doc.fileName,
                content: doc.getText().slice(0, 2000), // 2000 chars max for privacy
                language: doc.languageId,
            })
        })
    )

    // 3. Idle detection - reset timer on every keystroke
    ctx.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(() => resetIdleTimer())
    )

    // 4. Register command to open PME chat in browser
    ctx.subscriptions.push(
        vscode.commands.registerCommand('pme.openChat', () => {
            vscode.env.openExternal(vscode.Uri.parse('http://localhost:5173'))
        })
    )

    resetIdleTimer() // start idle timer immediately on activation
}

export function deactivate(): void {
    if (idleTimer) clearTimeout(idleTimer)
}
