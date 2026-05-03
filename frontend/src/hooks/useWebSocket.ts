/**
 * useWebSocket hook — stub for Phase 1. Full streaming in Phase 2.
 */

export function useWebSocket() {
    // Stub: WebSocket streaming will be implemented in Phase 2
    return {
        connected: false,
        connect: (_sessionId: string) => { },
        disconnect: () => { },
    }
}
