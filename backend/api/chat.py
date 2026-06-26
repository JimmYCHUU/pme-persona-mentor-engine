"""Chat API — main conversation endpoint with streaming support."""

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from graph.orchestrator import pme_graph
from graph.nodes.mastery_node import process_mastery_event
from graph.nodes.persona_node import persona_node as _persona_node_fn, _get_available_mentors, _build_boundary_instruction, SOCRATIC_INSTRUCTIONS
from services.persona_service import PersonaService
from services.llm_service import llm_service
from models.schemas import ChatRequest
import uuid
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/message', response_model=dict)
async def send_message(req: ChatRequest,
                       background_tasks: BackgroundTasks):
    """
    Main chat endpoint. Runs the full LangGraph pipeline.
    Triggers mastery_event processing as a BackgroundTask AFTER response.
    Returns: {success, data: ChatResponse, error}
    """
    initial_state = {
        'session_id': req.session_id or str(uuid.uuid4()),
        'persona_id': req.persona_id,
        'user_message': req.message,
        'workspace_event': None,
        'is_returning_user': False,
        'session_snapshot': None,
        'mastery_summary': None,
        'etm_context': None,
        'etm_matched': False,
        'deviation_score': 0.0,
        'socratic_level': 0,
        'vault_citation': None,
        'mastery_event': None,
        'raw_llm_response': '',
        'styled_response': '',
        'guardian_flagged': False,
        'final_response': '',
        'mode': req.mode or 'deep_dive',
    }

    try:
        result = await pme_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f'Graph execution failed: {e}', exc_info=True)
        return {'success': False, 'data': None, 'error': str(e)}

    # Debug: log key state fields
    final = result.get('final_response') or ''
    styled = result.get('styled_response') or ''
    raw = result.get('raw_llm_response') or ''

    if not final:
        logger.warning(
            f'Empty final_response! '
            f'styled_response="{styled[:100]}", '
            f'raw_llm_response="{raw[:100]}", '
            f'guardian_flagged={result.get("guardian_flagged")}'
        )
        # Fallback: use styled_response or raw_llm_response
        final = styled or raw or (
            'The AI provider is currently rate-limited (free tier). '
            'Please wait 30-60 seconds and try again.'
        )

    # Schedule mastery update as BackgroundTask (non-blocking)
    if result.get('mastery_event'):
        background_tasks.add_task(
            process_mastery_event, result['mastery_event']
        )

    return {
        'success': True,
        'data': {
            'response': final,
            'socratic_level': result.get('socratic_level', 0),
            'vault_citation': result.get('vault_citation'),
            'guardian_flagged': result.get('guardian_flagged', False),
            'session_id': result.get('session_id', ''),
        },
        'error': None,
    }


@router.post('/stream')
async def stream_message(req: ChatRequest):
    """
    SSE streaming endpoint. Runs the pipeline for context (socratic, vault,
    ETM), then streams the persona LLM response token-by-token.

    SSE format:
      data: {"type":"meta","socratic_level":1,"vault_citation":null,"session_id":"..."}
      data: {"type":"token","content":"Hello"}
      data: {"type":"token","content":" there"}
      data: [DONE]
    """
    session_id = req.session_id or str(uuid.uuid4())

    async def event_generator():
        try:
            # --- Run pipeline nodes for context (except persona LLM call) ---
            # Build initial state
            initial_state = {
                'session_id': session_id,
                'persona_id': req.persona_id,
                'user_message': req.message,
                'workspace_event': None,
                'is_returning_user': False,
                'session_snapshot': None,
                'mastery_summary': None,
                'etm_context': None,
                'etm_matched': False,
                'deviation_score': 0.0,
                'socratic_level': 0,
                'vault_citation': None,
                'mastery_event': None,
                'raw_llm_response': '',
                'styled_response': '',
                'guardian_flagged': False,
                'final_response': '',
                'mode': req.mode or 'deep_dive',
            }

            # Run memory, etm, socratic nodes via the graph
            # We run the full graph but will ignore its final_response
            # and instead stream our own LLM call
            from graph.nodes.memory_node import memory_node
            from graph.nodes.etm_node import etm_node
            from graph.nodes.socratic_node import socratic_node

            mem_result = await memory_node(initial_state)
            initial_state.update(mem_result)

            etm_result = await etm_node(initial_state)
            initial_state.update(etm_result)

            soc_result = await socratic_node(initial_state)
            initial_state.update(soc_result)

            # Build the persona system prompt (same logic as persona_node)
            persona_svc = PersonaService()
            persona = await persona_svc.get_persona(req.persona_id)

            if not persona:
                yield f"data: {json.dumps({'type': 'token', 'content': 'Mentor not found. Please select a mentor first.'})}\n\n"
                yield "data: [DONE]\n\n"
                return

            system_prompt = persona.get("system_prompt", "You are a helpful mentor.")

            # Add expertise boundary
            available_mentors = await _get_available_mentors(req.persona_id)
            boundary = _build_boundary_instruction(persona, available_mentors)
            system_prompt += boundary

            # Socratic instruction
            level = initial_state.get("socratic_level", 0)
            socratic_inst = SOCRATIC_INSTRUCTIONS.get(level, "")
            if socratic_inst:
                system_prompt += socratic_inst

            # Vault citation
            vault_citation = initial_state.get("vault_citation")
            if vault_citation:
                system_prompt += f"\n\n[REFERENCE] The student's own materials contain this relevant passage: {vault_citation}\nWeave this reference naturally into your response when appropriate."

            # ETM context
            etm_context = initial_state.get("etm_context")
            if etm_context:
                system_prompt += f"\n\n[WORKSPACE CONTEXT] The student is working on something related to: {etm_context}\nConnect your teaching to this specific context."

            # History
            history = []
            if initial_state.get("session_snapshot"):
                history = initial_state["session_snapshot"].get("history", [])

            # Send metadata first
            meta = {
                "type": "meta",
                "socratic_level": level,
                "vault_citation": vault_citation,
                "session_id": session_id,
            }
            yield f"data: {json.dumps(meta)}\n\n"

            # Stream the LLM response
            async for token in llm_service.chat_stream(
                message=req.message,
                system=system_prompt,
                history=history,
            ):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
