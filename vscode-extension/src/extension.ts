import * as vscode from 'vscode'
import axios from 'axios'

const PME_URL = 'http://localhost:8000/workspace/event'
let idleTimer: NodeJS.Timeout | undefined
const IDLE_MS = 300_000

async function postEvent(payload: object): Promise<void> {
  try {
    await axios.post(PME_URL, payload, { timeout: 3000 })
  } catch {
    // never crash VS Code
  }
}

function isError(text: string): boolean {
  return /error|exception|traceback|failed|syntaxerror|typeerror/i.test(text)
}

function resetIdleTimer(): void {
  if (idleTimer) clearTimeout(idleTimer)
  idleTimer = setTimeout(() => {
    void postEvent({ type: 'idle', duration_seconds: 300 })
  }, IDLE_MS)
}

export function activate(ctx: vscode.ExtensionContext): void {
  ctx.subscriptions.push(
    // @ts-ignore - terminal data event typing may vary across VS Code versions
    vscode.window.onDidWriteTerminalData((e) => {
      if (isError(e.data)) {
        void postEvent({ type: 'terminal_error', content: e.data.slice(0, 1000) })
      }
    }),
  )

  ctx.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument((doc: vscode.TextDocument) => {
      void postEvent({
        type: 'file_save',
        file: doc.fileName,
        content: doc.getText().slice(0, 2000),
        language: doc.languageId,
      })
    }),
  )

  ctx.subscriptions.push(vscode.workspace.onDidChangeTextDocument(() => resetIdleTimer()))

  ctx.subscriptions.push(
    vscode.commands.registerCommand('pme.openChat', () => {
      void vscode.env.openExternal(vscode.Uri.parse('http://localhost:5173'))
    }),
  )

  resetIdleTimer()
}

export function deactivate(): void {
  if (idleTimer) clearTimeout(idleTimer)
}
