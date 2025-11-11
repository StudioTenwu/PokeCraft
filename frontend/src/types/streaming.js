/**
 * @file Server-Sent Events contracts for agent creation streaming
 *
 * This file defines the event types and data shapes that the server
 * can send during the agent creation process. This serves as the
 * contract between client and server.
 */

/**
 * Base SSE event structure
 * @typedef {Object} SSEEvent
 * @property {string} event - Event type name
 * @property {Object} data - Event payload (varies by event type)
 */

/**
 * Agent creation stream events
 * @typedef {Object} AgentCreationEvents
 */

/**
 * LLM generation started
 * @typedef {Object} LLMStartEvent
 * @property {'llm_start'} event
 * @property {Object} data
 * @property {string} data.status - Always "generating"
 * @property {number} [data.timestamp] - Optional timestamp
 */

/**
 * LLM generation completed
 * @typedef {Object} LLMCompleteEvent
 * @property {'llm_complete'} event
 * @property {Object} data
 * @property {string} data.name - Generated agent name
 * @property {string} data.type - Agent type
 * @property {string[]} data.abilities - List of abilities
 * @property {Object} data.stats - Agent stats (hp, attack, defense, speed)
 * @property {string} [data.personality] - Optional personality description
 */

/**
 * Avatar generation started
 * @typedef {Object} AvatarStartEvent
 * @property {'avatar_start'} event
 * @property {Object} data
 * @property {string} data.status - Always "generating"
 * @property {string} data.style - Avatar style being generated
 */

/**
 * Avatar generation progress update
 * @typedef {Object} AvatarProgressEvent
 * @property {'avatar_progress'} event
 * @property {Object} data
 * @property {number} data.progress - Progress percentage (0-100)
 * @property {string} [data.step] - Current generation step description
 */

/**
 * Avatar generation completed
 * @typedef {Object} AvatarCompleteEvent
 * @property {'avatar_complete'} event
 * @property {Object} data
 * @property {string} data.url - URL to the generated avatar image
 * @property {string} data.filename - Avatar filename
 */

/**
 * Entire agent creation process completed
 * @typedef {Object} CompleteEvent
 * @property {'complete'} event
 * @property {Object} data
 * @property {Object} data.agent - Complete agent object
 * @property {string} data.agent.id - Agent UUID
 * @property {string} data.agent.name - Agent name
 * @property {string} data.agent.type - Agent type
 * @property {string} data.agent.avatar_url - Avatar URL
 * @property {Object} data.agent.stats - Agent stats
 * @property {string[]} data.agent.abilities - Abilities list
 */

/**
 * Error occurred during agent creation
 * @typedef {Object} ErrorEvent
 * @property {'error'} event
 * @property {Object} data
 * @property {string} data.message - Error message
 * @property {string} [data.code] - Error code
 * @property {Object} [data.details] - Additional error details
 */

/**
 * Union type of all possible agent creation events
 * @typedef {LLMStartEvent | LLMCompleteEvent | AvatarStartEvent |
 *           AvatarProgressEvent | AvatarCompleteEvent | CompleteEvent |
 *           ErrorEvent} AgentCreationStreamEvent
 */

/**
 * Callback function signatures for agent creation stream
 * @typedef {Object} AgentCreationCallbacks
 * @property {(data: LLMStartEvent['data']) => void} [onLLMStart]
 * @property {(data: LLMCompleteEvent['data']) => void} [onLLMComplete]
 * @property {(data: AvatarStartEvent['data']) => void} [onAvatarStart]
 * @property {(data: AvatarProgressEvent['data']) => void} [onAvatarProgress]
 * @property {(data: AvatarCompleteEvent['data']) => void} [onAvatarComplete]
 * @property {(data: CompleteEvent['data']) => void} [onComplete]
 * @property {(error: Error) => void} [onError]
 */

/**
 * Event name to callback mapping for internal use
 * @type {Record<string, keyof AgentCreationCallbacks>}
 */
export const EVENT_CALLBACK_MAP = {
  'llm_start': 'onLLMStart',
  'llm_progress': 'onLLMProgress',
  'llm_complete': 'onLLMComplete',
  'avatar_start': 'onAvatarStart',
  'avatar_progress': 'onAvatarProgress',
  'avatar_complete': 'onAvatarComplete',
  'complete': 'onComplete'
}

/**
 * List of all valid event types for validation
 * @type {string[]}
 */
export const VALID_EVENT_TYPES = [
  'llm_start',
  'llm_progress',
  'llm_complete',
  'avatar_start',
  'avatar_progress',
  'avatar_complete',
  'complete',
  'error'
]

/**
 * Validate that an event matches the contract
 * @param {string} eventType - Event type to validate
 * @param {any} data - Event data to validate
 * @returns {boolean} True if valid
 */
export function validateEvent(eventType, data) {
  if (!VALID_EVENT_TYPES.includes(eventType)) {
    console.warn(`Unknown event type: ${eventType}`)
    return false
  }

  // Basic validation - you can make this stricter
  if (!data || typeof data !== 'object') {
    console.warn(`Invalid data for event ${eventType}:`, data)
    return false
  }

  return true
}
