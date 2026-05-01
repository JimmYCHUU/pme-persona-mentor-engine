**PERSONA MENTOR ENGINE**

_Software Requirements Specification_

──────────────────────────────────────────────

Final Version · Consolidates SRS v1.0 through v4.0 · Complete & Self-Contained

| **Field**            | **Value**                                                    | **Note**                      |
| -------------------- | ------------------------------------------------------------ | ----------------------------- |
| **Version**          | Final (4.0 equivalent)                                       | All prior versions superseded |
| **Classification**   | Private - Single User System                                 | No multi-tenancy at MVP       |
| **Primary Audience** | ChatGPT Codex, GitHub Copilot, Claude Code, human developers | Machine-readable format       |
| **Target Hardware**  | Ubuntu/Debian, 8 GB RAM, no GPU                              | llama3.2:3b via Ollama        |
| **Framework**        | LangGraph orchestration + LlamaIndex RAG                     | Docker for dev environment    |
| **Methodology**      | Superpowers framework + Context7 MCP                         | TDD, YAGNI, DRY mandated      |

# **0\. Document Information**

_MACHINE-READABLE NOTE FOR CODEX: This SRS is the definitive WHAT document. It defines every requirement. The companion SDD (Final Version) is the HOW document - it contains exact code, exact commands, and zero ambiguity. Read this SRS first to understand intent. Then follow the SDD exclusively for implementation. If any requirement in this SRS conflicts with the SDD, the SRS wins on intent; the SDD wins on implementation detail._

This document consolidates all SRS versions (v1.0 through v4.0) into a single, authoritative, self-contained specification. Every requirement is present. Nothing is referenced externally. No prior SRS version needs to be consulted.

## **0.1 Version History**

| **Version** | **Key Additions**      | **Detail**                                                                                                                                                           |
| ----------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| v1.0        | Foundation             | Core concept: Bimodal RAG, Socratic Interruption Engine, Active State Resume, Soul-Sync Interface, Guardian Overlay, privacy-first architecture.                     |
| v2.0        | 5 Modules              | Formalised into 5 modules: Omni-Ingestor, Persona Synthesis, Socratic Engine, Session Memory, Guardian Overlay. LangGraph orchestration. 4-phase build.              |
| v3.0        | Mastery + ETM          | Module 6 (Mastery Tracking), Module 7 (Proof of Mastery). Ethical Time Machine reframing. Sacred Space UI. Docker. 5-phase build. mastery_node, cert_node, etm_node. |
| v4.0        | Methodology            | Section 8: Superpowers framework + Context7 MCP mandated. NFR-011 through NFR-015 added. TDD formalised for all 7 LangGraph nodes.                                   |
| **Final**   | **Full consolidation** | This document. All versions merged. Complete. Self-contained. No external references needed.                                                                         |

# **1\. System Overview**

## **1.1 What the PME Is**

The Persona Mentor Engine (PME) is a private, local-first AI workspace that clones the intellectual DNA of any real-world expert and places that mentor beside the user as they learn and work. It is NOT a chatbot, a course platform, or a generic AI assistant.

The PME is a Digital Twin Mentorship environment - a persistent, stateful workspace where the user can:

- Learn a skill by being guided by the chosen expert's actual reasoning and methods
- Chat casually with the mentor persona as a knowledgeable friend
- Work on projects while the mentor watches silently and intervenes Socratically
- Resume sessions exactly where they left off with full context recall and cumulative mastery awareness
- Receive in-character Proof of Mastery certifications when a concept is genuinely understood

## **1.2 The Ethical Time Machine - Product Identity**

_This is the headline differentiator of PME. Every competitor product (Rocky.ai, Sensay, Twin Protocol) gives the learner a frozen snapshot of the mentor at their most famous. PME is fundamentally different: Your mentor is smarter than the real person. They have ALL the original wisdom - PLUS the knowledge of what they got wrong, what has changed, and what they would tell their past self. You train with the version that already survived their own mistakes._

This has two technical consequences that are non-negotiable:

- The Guardian Overlay (Module 5, now called Ethical Time Machine) is NOT a safety filter. It is the product's core intellectual value proposition. Outdated advice is actively evolved in the mentor's own voice, never blocked with a generic warning.
- The mentor proactively flags paradigm shifts, deprecated practices, and legal/technical evolution as part of teaching - not as an afterthought.

## **1.3 The Sacred Space - UI Identity**

PME does not open as a chat interface. It opens as a workspace. The distinction is intentional and experiential. Every other AI tool is a chat window. PME is a private study room with a mentor who is already at the desk, already thinking about your work, already ready with a question.

The opening ritual signals to the user: this is different. This is not a tool. This is a practice.

## **1.4 Bimodal Architecture - SOUL + BRAIN**

| **Layer**   | **The SOUL (How mentor speaks)**                                                | **The BRAIN (What mentor knows)**                                             | **Priority rule**                                                    |
| ----------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Source**  | Public: social media, YouTube, GitHub, interviews                               | Private: paid courses, PDFs, personal notes, private memos                    | Brain ALWAYS overrides Soul on factual/technical matters             |
| **Storage** | Persona Vector Store - lightweight, permanent, always loaded                    | Local ChromaDB - encrypted at rest, never leaves machine                      | Soul = Truth_50 Brain = Truth_100                                    |
| **Example** | Network Chuck's coffee-sipping urgency, vocabulary, sarcasm level, catchphrases | TCM course: specific OSINT methods, preferred tools, step-by-step methodology | If tweet says X but course says Y, the AI teaches Y in Chuck's voice |

# **2\. System Modules**

_ARCHITECTURE RULE: Each module is a separate, independently testable component orchestrated by the LangGraph State Machine (Section 3). Build in the order listed. Module N must be complete and tested before Module N+1 begins. Modules 6 and 7 require Module 4 to be complete._

## **Module 1 - Omni-Ingestor (The Digital Archeology Engine)**

Builds the mentor's complete knowledge and personality profile from all available sources. Runs during onboarding and can be refreshed on demand.

### **1A - Public Fingerprint Pipeline (SOUL data)**

**REQ-INGEST-001: Social Media Scraper**

- Supported platforms: X (Twitter), LinkedIn, Facebook, Instagram
- Extract: post text, reply style, emoji usage, argument patterns, tone under pressure
- DO NOT just collect facts - extract sentence structure, vocabulary density, sarcasm markers
- Tag each item: platform, date, sentiment_score, topic_category, authority=50

**REQ-INGEST-002: YouTube & Video Transcript Analyzer**

- Accept: YouTube channel URL or individual video URLs
- Transcribe locally using Whisper (base or small model ONLY - never large)
- Analyze: speech pacing, filler words, catchphrases, how mentor handles mistakes in live demos
- Use a Vision-Language Model on screen-share segments to extract tool preferences and workflow habits

**REQ-INGEST-003: GitHub / Technical Repository Analyzer**

- If mentor has public repositories, ingest commit messages, README style, code comments
- Extract: preferred languages, naming conventions, architecture preferences

**REQ-INGEST-004: Linguistic Profile Builder**

After all public data is collected, build the Persona Vector - a compact, permanent representation of the mentor's soul. Must include:

- Vocabulary map: unique words, expert slang, banned phrases (words they never use)
- Sentiment profile: default enthusiasm level (0-100), aggression level (0-100), humor style
- Philosophy map: recurring beliefs, rules they live by that are not in textbooks
- Reaction model: how the mentor responds to student failure, confusion, repeated mistakes
- Few-shot examples: 10+ real mentor dialogue samples with user prompt and mentor reply pairs

### **1B - Private Wisdom Vault Pipeline (BRAIN data)**

**REQ-INGEST-005: Private Vault Ingestion Portal**

- Accept: MP4 video, PDF, EPUB, plain text, MP3/M4A audio
- MP4/MP3: transcribe via Whisper locally (base/small only)
- PDF: extract text via pypdf
- Chunk all content into semantically meaningful segments (NOT fixed token sizes)
- Vectorize and store in local ChromaDB: collection name = vault\_{persona_id}
- NEVER upload vault content to any external server
- Tag each chunk: source_file, chapter/timestamp, topic, confidence_score, authority=100

**REQ-INGEST-006: Authority Ranking System**

When a user query retrieves conflicting information from multiple sources, rank by:

- Private Vault - paid course content: Truth_100
- Private Vault - user's own notes and uploads: Truth_95
- Public technical content - GitHub repos, whitepapers, documentation: Truth_70
- Public personality content - social media, YouTube: Truth_50

### **1C - Gap-Fill Interview System**

**REQ-INGEST-007: Automated Gap Detection**

- After ingestion, detect if the soul model is missing: emotional reaction data, failure handling style, teaching preferences, peer interaction style
- Detect if brain model is missing key topic areas relative to the user's stated learning goals

**REQ-INGEST-008: User Interview Flow**

- Generate 3-5 targeted questions to fill identified gaps
- Accept text responses OR short voice recording (30-second max)
- From voice: extract emotional sentiment and adjective clusters to seed personality weights
- Store all gap-fill answers as high-authority persona overrides (Truth_95)

_EXAMPLE output of gap-fill question: 'I have mapped his technical skills from the TCM course and his personality from social media. But I have no data on how he reacts when a student fails a basic concept twice. Does he get disappointed, use humor, or apply pressure? How should I handle your mistakes?'_

## **Module 2 - Persona Synthesis Layer (The Soul Engine)**

Makes the AI speak, think, and react exactly like the chosen mentor. A wrapper layer on top of the base LLM. The persona layer changes HOW the answer is expressed, not the underlying factual content.

**REQ-PERSONA-001: Base LLM Selection**

- Use locally-hosted Ollama with llama3.2:3b (8 GB RAM target) or Llama 3 70B (high-spec machines)
- RATIONALE: Local open-source models do not have corporate-polite guardrails. This is required for authentic, unfiltered mentor tone.
- NO cloud LLM may be used for inference under any circumstances

**REQ-PERSONA-002: Persona System Prompt (Few-Shot Style Transfer)**

- DO NOT fine-tune the base model - use few-shot prompting with 10-20 real mentor dialogue examples
- System prompt must include: vocabulary list, tone calibration (abrasiveness slider value), philosophy gates, reaction examples from gap-fill interview
- CRITICAL: The persona layer is a FILTER on LLM output. It changes HOW the answer is expressed, not what the answer factually is. Socratic content is injected BEFORE persona styling.

**REQ-PERSONA-003: Persona Dashboard (User Controls)**

| **Slider**           | **Range** | **At 0**                                                       | **At 100**                                                         |
| -------------------- | --------- | -------------------------------------------------------------- | ------------------------------------------------------------------ |
| persona_abrasiveness | 0-100     | Gentle Professor - encouraging, patient, guides with questions | Drill Sergeant - blunt, creates pressure, scolds repeated mistakes |
| persona_proactivity  | 0-100     | Silent - only responds when asked directly                     | Maximum - interrupts frequently based on idle time and deviations  |
| persona_explainDepth | 0-100     | Pure practice - minimal explanation, just do it                | Deep theory - explains the Why behind every recommendation         |

**REQ-PERSONA-004: Authentic Greeting System**

The mentor's greeting when the user returns must satisfy all three of the following:

- Authority: the mentor TELLS the user what needs to be done. Does not ask 'How can I help?'
- Atmosphere: the greeting includes the mentor's signature habits (coffee, terminal, calm studio tone)
- Bias: the mentor immediately expresses an opinion on the current project or the user's progress

_EXAMPLE - Network Chuck persona on return: 'Stop everything. You left that listener hanging mid-function. I have been staring at it. Grab a coffee, sit down, and let us fix the buffer logic before you touch anything else. Are we finishing this today or not?'_

**REQ-PERSONA-005: Friend Mode**

- Triggered by user saying a break phrase or explicitly toggling the mode switch
- Workspace UI theme softens (dark urgent amber → warm ambient blue)
- Mentor shifts from technical coaching to casual conversation
- Mentor stays in character - Friend Mode changes purpose, not persona
- Socratic monitoring is SUSPENDED in Friend Mode
- Mastery tracking events are SUSPENDED in Friend Mode

## **Module 3 - Socratic Interruption Engine (Mastery-Aware)**

The core pedagogical differentiator. Instead of waiting to be asked, the mentor monitors the user's workspace and intervenes using the Socratic method. Goal: force the user to think, not give them the answer.

**REQ-SOCRATIC-001: Workspace State Monitor**

- Monitor: terminal output, IDE open files, terminal error messages, idle time
- Requires a lightweight OS-level agent (VS Code extension or terminal plugin)
- The monitor feeds a live event stream to the Socratic Orchestrator node
- DO NOT give the agent access to file contents beyond the first 2000 characters per file

**REQ-SOCRATIC-002: Deviation Threshold Engine (Mastery-Aware)**

- System maintains a Gold Standard path (how the expert would approach the current task)
- Compares Gold Standard to the user's Current Path in real time
- If deviation_score < threshold_alpha: silent observation - do nothing
- If deviation_score >= threshold_alpha: check MasteryLedger for this concept's status
- If concept status is STRUGGLING in MasteryLedger: start at Level 2 (skip Level 1)
- If lifetime_failure_count >= 5 for concept: start at Level 3 (Critique) immediately
- threshold_alpha is adjustable via the persona_proactivity slider

**REQ-SOCRATIC-003: The Socratic Ladder**

| **Lvl** | **Name**     | **Mentor Action**                                                                                                          | **Trigger Condition**                                                                  | **Answer given?**  |
| ------- | ------------ | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------ |
| 0       | Silent       | Observation only. Mastery event logged as neutral encounter.                                                               | deviation_score < threshold                                                            | No                 |
| 1       | The Nudge    | Highlights the area. Asks ONE probing question about fundamental constraint. Does NOT name the error.                      | deviation >= threshold AND concept status = encountered or attempted                   | No                 |
| 2       | The Hint     | References a SPECIFIC piece of Private Vault content relevant to the problem. Points to it - does not explain it.          | deviation >= threshold AND (concept = struggling OR mastery_score < 0.4)               | No                 |
| 3       | The Critique | Explains the consequence of the current approach. Still NO fix given. Creates pressure appropriate to abrasiveness slider. | deviation >= threshold AND (lifetime_failure_count >= 5 OR struggling for 2+ sessions) | No                 |
| 4       | The Reveal   | Direct solution given ONLY after 3 failures in the CURRENT session. Immediately asks: 'Now tell me WHY that works.'        | session_failure_count >= 3 for this concept                                            | YES - then ask WHY |

**REQ-SOCRATIC-004: Explainability Requirement**

- Every Socratic intervention at Level 2 or higher MUST cite a specific source from the Private Wisdom Vault
- Citation must include: source_file, chapter/timestamp, relevant concept
- If NO vault source exists for the topic: mentor says so explicitly. No hallucinated citations. Ever.

**REQ-SOCRATIC-005: Idle Trigger**

- If user has been idle for more than idle_trigger_seconds (default 300s), mentor checks in
- Check-in is persona-appropriate - not a generic AI ping
- Idle trigger also logs a passive_encounter event on any concept open in workspace

**REQ-SOCRATIC-006: Mastery Feedback Loop**

- After each Socratic exchange, socratic_node emits a mastery_event to mastery_node
- mastery_event contains: concept_key, outcome (correct/incorrect/partial), socratic_level_used, session_id
- mastery_node processes this event ASYNCHRONOUSLY - never in the main response path

## **Module 4 - Active State Resume (Session Memory)**

The mentor never forgets. Every session is saved in full and restored on return. In the resume greeting, the mentor references not just the last session but the user's entire learning journey.

**REQ-MEMORY-001: Tri-Tier + Mastery Memory Architecture**

| **Tier** | **Name**            | **Contents**                                                                             | **Query Trigger**                                                          |
| -------- | ------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1        | The Library         | Full vector DB of all ingested content: transcripts, courses, PDFs, code                 | Queried on specific technical questions                                    |
| 2        | The Persona Vector  | Compact permanent set: personality traits, philosophies, catchphrases, reaction patterns | Always loaded in every interaction                                         |
| 3        | The Work-Stream     | Current session: open files, terminal state, recent actions, active project              | Queried continuously by Socratic Monitor                                   |
| **4**    | **The Mastery Map** | \[v3\] Cross-session concept mastery ledger: understood, struggling, mastered            | Queried by Socratic node on deviation check; summarised in resume greeting |

**REQ-MEMORY-002: Session State Schema**

{

"session_id": "uuid-v4",

"persona_id": "string",

"created_at": "ISO-8601",

"updated_at": "ISO-8601",

"mode": "deep_dive | friend_mode",

"active_project": { "name": "str", "description": "str", "current_phase": "str" },

"work_state": {

"open_files": \["string"\],

"last_terminal_error": "string | null",

"unresolved_critiques": \["string"\],

"last_vault_citation": "string"

},

"mentor_assessment": {

"summary": "string",

"user_strengths": \["string"\],

"user_weaknesses": \["string"\],

"next_steps": \["string"\]

},

"mastery_context": {

"top_struggling": \[{ "concept_key": "str", "failure_count": 0 }\],

"new_certs_since_last_session":\["concept_label"\]

},

"chat_history": \[{ "role": "user|assistant", "content": "str",

"timestamp": "ISO-8601", "socratic_level": 0 }\],

"failure_counts": { "concept_key": 0 }

}

**REQ-MEMORY-003: Contextual Re-Sync Greeting**

When the user returns, the Resume Agent reads the last session snapshot AND the Mastery Ledger to generate a greeting that:

- Addresses the user by name or a mentor-appropriate shorthand
- States exactly what was being worked on in the last session
- Identifies the top 1-2 concepts currently in STRUGGLING status and references them explicitly
- Flags any new Proof of Mastery certifications earned since last session
- Presents the next 3 steps in the mentor's authentic voice

_EXAMPLE - Network Chuck on return with struggling concept: 'Stop. Before you touch anything - I looked back at our last three sessions. You keep flinching on buffer logic. Not just yesterday. Three times across two weeks. That is a pattern. We are fixing that today before anything else. Get coffee. Open the terminal. And do NOT skip the explanation this time.'_

**REQ-MEMORY-004: Project Continuation Flow**

- On session resume, display a visual step-by-step roadmap of incomplete tasks
- User must explicitly confirm: Continue this project OR Start something new
- Switching projects saves current state and archives it - resumable later

**REQ-MEMORY-005: Auto-Save**

- Session snapshot auto-saved every 60 seconds while the workspace is active
- Full snapshot saved on graceful exit
- Session state must survive application crashes (auto-save covers this)

## **Module 5 - Ethical Time Machine (The Evolved Guardian)**

_REFRAMED IN v3.0: This module was previously called 'Guardian Overlay (Safety Layer)'. That framing was wrong. The Ethical Time Machine is the headline product differentiator - not a speed bump. Every competitor gives a frozen snapshot. PME gives the version that already learned from their mistakes._

**REQ-ETM-001: The Time Machine Database (evolution_db.json)**

- During fingerprint ingestion, extract and store evolution events for the persona
- An evolution event is: a paradigm shift, a deprecated practice, a public statement of regret, a technique the mentor stopped recommending
- Schema: { concept_key, old_advice, new_advice, evolution_year, evidence_sources\[\] }
- Stored locally at: data/personas/{persona_id}/evolution_db.json
- evolution_db.json is built from local fingerprint analysis ONLY - no external AI service

**REQ-ETM-002: Proactive Evolution Injection**

- etm_node runs BEFORE socratic_node in every exchange
- If the user's current topic matches a concept in evolution_db, inject evolution context into state
- The mentor proactively mentions the evolution - does not wait to be asked
- Evolution is framed as the mentor's own growth: 'I used to recommend X. I was wrong. Here is why.'

**REQ-ETM-003: Shadow Classifier Backstop (Last Resort)**

- A DistilBERT-based classifier runs locally on every mentor response
- This is the LAST line of defence - only activates when etm_node has not already handled the issue
- FLAGGED_CATEGORIES: illegal_instruction, dangerous_technical, pii_leak
- If flagged: generate an in-character rewrite via Ollama - never use a generic safety warning
- Load the classifier LAZILY - only on first use, not at import time (memory constraint)

_EXAMPLE in-character rewrite: 'Look, I know what I used to say about brute-forcing this - I was wrong, and the landscape has changed. Modern detection systems will flag that IP in under three seconds. We are going to do this the evolved way - smarter, stealthier, and you will not end up with a lawyer. Let me show you the current method.'_

## **Module 6 - Cross-Session Mastery Tracking \[Added v3.0\]**

The PME tracks the user's mastery of individual concepts across all sessions. This is not session-level memory - it is longitudinal learning analytics. It makes the Socratic engine smarter over time.

**REQ-MASTERY-001: MasteryLedger Schema (SQLite table)**

MasteryLedger:

concept_id TEXT PRIMARY KEY (uuid)

persona_id TEXT (FK → PersonaProfile)

concept_key TEXT (machine-readable, e.g. 'tcp_handshake')

concept_label TEXT (human-readable, e.g. 'TCP Handshake')

status TEXT ('encountered'|'attempted'|'struggling'|'mastered')

mastery_score REAL DEFAULT 0.0 (0.0 → 1.0, deterministic formula)

encounter_count INTEGER DEFAULT 0

success_count INTEGER DEFAULT 0

failure_count INTEGER DEFAULT 0 (lifetime, across all sessions)

sessions_tested TEXT (JSON array of session_ids)

first_seen TEXT (ISO-8601)

last_tested TEXT (ISO-8601)

vault_sources TEXT (JSON array of citation strings)

mentor_notes TEXT DEFAULT NULL

**REQ-MASTERY-002: Mastery Status Rules**

| **Status**  | **Condition**                                                        | **Socratic Impact**                                                              |
| ----------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| encountered | mastery_score < 0.2                                                  | Socratic starts at Level 1 on next deviation                                     |
| attempted   | 0.2 <= score < 0.4                                                   | Socratic starts at Level 1 on next deviation                                     |
| struggling  | score &lt; 0.4 AND failure_count &gt;= 3                             | Socratic starts at Level 2 (skips Level 1) on next deviation                     |
| mastered    | mastery_score >= 0.8 AND sessions_tested >= 3 AND success_count >= 5 | Socratic does not activate for this concept. Eligible for Proof of Mastery cert. |

**REQ-MASTERY-003: mastery_node Behaviour**

- Receives mastery_event from socratic_node ASYNCHRONOUSLY
- Extracts concept_key from the event (via short LLM call with lightweight prompt)
- Updates MasteryLedger: mastery_score, status, counts, sessions_tested
- SCORE_INCREMENT and SCORE_DECREMENT must be NAMED CONSTANTS, not magic numbers
- mastery_score = clamp(current_score + delta, 0.0, 1.0) - never below 0, never above 1
- After update: calls should_certify() - if conditions met, triggers cert_node
- MUST NEVER add latency to the user-facing response path - runs as a background task

**REQ-MASTERY-004: Mastery Map UI**

- A sidebar or panel view showing all tracked concepts for the active persona
- Each concept shown as a card: label, mastery_score progress bar, status badge, session_count
- Status badge colours: encountered=grey, attempted=blue, struggling=amber, mastered=green
- STRUGGLING concepts shown with a count badge in the sidebar navigation item

## **Module 7 - Proof of Mastery Certification \[Added v3.0\]**

When the user genuinely masters a concept - not by quiz, but by demonstrating it across multiple sessions in different contexts - the mentor issues an in-character certification that serves as a new kind of credential.

**REQ-CERT-001: Certification Trigger Conditions**

ALL of the following must be true simultaneously before a certification is generated:

- mastery_score >= 0.8 for the concept
- sessions_tested >= 3 (concept tested in at least 3 separate sessions)
- success_count >= 5 (at least 5 successful interactions on this concept across all sessions)
- The concept has NOT already been certified (no existing cert for this persona + concept_key)

**REQ-CERT-002: In-Character Certification Generation**

The cert_node generates the certification text using OllamaService. The prompt must instruct the LLM to:

- Speak entirely as the mentor persona - no AI voice, no 'Congratulations from the system'
- Reference specific evidence from the sessions: 'The last three times I pushed you on this, you had it'
- Express the mentor's genuine standard: what mastery means TO THEM for this concept
- State clearly that the user is trusted to work on this independently

_EXAMPLE - Network Chuck certifying TCP Handshake: 'Alright. I have been watching. Three sessions, different contexts, different problems - every time I pushed you on the handshake, you had it. Not just reciting it - you reasoned through it. SYN, SYN-ACK, ACK: you understand why each step exists, not just what to type. I would hand you a production firewall rule to write right now and trust you not to leave a hole. That is what mastery means to me. You have got it.'_

**REQ-CERT-003: Certification Storage (SQLite + JSON)**

MasteryCertificate:

cert_id TEXT PRIMARY KEY (uuid)

persona_id TEXT (FK → PersonaProfile)

concept_key TEXT (FK to MasteryLedger)

concept_label TEXT

issued_at TEXT (ISO-8601)

mentor_statement TEXT (the in-character certification text)

evidence_summary TEXT (JSON: sessions_tested, success_count, mastery_score)

cert_json_path TEXT (path: data/mastery_certs/{persona_id}/{concept_key}.json)

delivered INTEGER DEFAULT 0 (0=pending, 1=delivered to user)

**REQ-CERT-004: Certification UI (MasteryCertModal)**

- Cert is delivered at the START of the NEXT session - never interrupting the current conversation
- MasteryCertModal: full-screen dark overlay, centred card
- Card: amber accent border, mentor name prominent, concept label as title, mentor_statement as body
- Two actions: 'Close' (ghost button) and 'Export as PDF' (local file save, no external upload)
- After closing: cert marked as delivered=1 in SQLite
- Earned certs visible in Mastery Map sidebar under the relevant concept card
- Resume greeting mentions new certs: 'You earned something since last time. Look at your Mastery Map.'

# **3\. LangGraph Orchestration**

## **3.1 Graph Nodes**

| **Node**      | **Module** | **Responsibility**                                                                                                                              |
| ------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| ingestor_node | Module 1   | Runs during onboarding only. Builds SOUL (Persona Vector) and BRAIN (ChromaDB vault). Also seeds evolution_db.json.                             |
| memory_node   | Module 4   | Reads session snapshot + Mastery Ledger summary. Generates mastery-enriched resume greeting on session start. Saves session on exit.            |
| etm_node      | Module 5   | Checks evolution_db for matches to current topic. Injects proactive evolution context if found. Runs BEFORE socratic_node.                      |
| socratic_node | Module 3   | Computes deviation score. Reads MasteryLedger for starting level. Triggers Socratic Ladder. Emits mastery_event ASYNCHRONOUSLY to mastery_node. |
| persona_node  | Module 2   | Loads persona profile. Builds few-shot system prompt. Calls OllamaService. Applies style-transfer filter to LLM response.                       |
| guardian_node | Module 5   | Runs shadow classifier. If flagged: rewrites response in-character via OllamaService. Runs LAST before response delivery.                       |
| mastery_node  | Module 6   | NOT in main graph. Runs as FastAPI BackgroundTask. Processes mastery_event. Updates MasteryLedger. Calls should_certify().                      |
| cert_node     | Module 7   | NOT in main graph. Called by mastery_node if should_certify() returns True. Generates and stores Proof of Mastery cert. Sets delivered=0.       |

## **3.2 Data Flow - Main Response Path**

User Input / Workspace Event

|

v

\[memory_node\] ← loads session state + Mastery Ledger summary

|

v

\[etm_node\] ← checks evolution_db, injects context if topic matches

|

v

\[socratic_node\] ← computes deviation + reads MasteryLedger for starting level

| \\

| \\→ emits mastery_event → \[mastery_node (BackgroundTask)\]

| \\→ \[cert_node (if conditions met)\]

v

\[persona_node\] ← builds system prompt + calls OllamaService

|

v

\[guardian_node\] ← shadow classifier + in-character rewrite if flagged

|

v

\[user_interface\] ← renders final_response + SocraticBadge + vault_citation

|

v

\[memory_node\] ← saves updated session state

_CRITICAL: mastery_node and cert_node run ASYNCHRONOUSLY as FastAPI BackgroundTasks. They MUST NEVER block or delay the main response path. The user sees the mentor response immediately. Mastery updates happen in the background. A Proof of Mastery certification modal appears at the START OF THE NEXT SESSION, not during the current conversation._

# **4\. User Interaction Flows**

## **4.1 The Sacred Space Opening Ritual \[v3.0\]**

- Application launches with a 1.5-second opening animation: the workspace materialises from black
- Ambient terminal glow effect - mentor's name appears as if typed on a terminal, character by character
- If a session exists: the mentor's resume greeting fades in BEFORE the chat pane is visible
- The user must explicitly 'sit down' (click a button or press Enter) to enter the workspace
- This intentional friction signals the beginning of a focused session - it is a feature, not a bug
- The workspace is a dedicated UI shell (WorkspaceShell.tsx) - chat is embedded within the workspace, not the reverse
- Focus Mode: when user is in Deep Dive mode, all UI outside the chat pane dims to 15% opacity

## **4.2 Onboarding Flow (First-Time Setup)**

- User opens PME. Sacred Space opening animation plays (cold start version).
- Mentor Selection screen: (A) Pre-built gallery of archetypes OR (B) Build from scratch by name/handle.
- Public Fingerprint Sweep: user enters YouTube URL, Twitter/LinkedIn handle. Ingestor runs.
- Private Vault Upload: user uploads course files (PDF, MP4, MP3, DOCX). Optional but strongly encouraged.
- Gap-Fill Interview: 3-5 questions generated by system based on ingestion gaps. User answers.
- Persona Sliders: user sets initial abrasiveness, proactivity, and explain depth values.
- Mastery Ledger Initialised: empty ledger created. System explains mastery tracking to user.
- Onboarding complete. System saves persona profile. Transitions to workspace.

## **4.3 Standard Desk Session Flow**

- User opens PME. Sacred Space opening ritual plays.
- Memory Node loads last session snapshot + Mastery Ledger summary.
- If pending Proof of Mastery cert: MasteryCertModal appears FIRST before anything else.
- Mentor delivers Contextual Re-Sync Greeting: last session context + top STRUGGLING concept + next steps.
- User confirms: Continue current project OR start new topic.
- ETM Node checks evolution_db. If current project involves evolved concepts, mentor notes them proactively.
- Socratic Monitor begins watching workspace. MasteryLedger consulted for ladder starting level.
- User works. Mentor observes silently. Socratic Ladder triggers only on threshold breach.
- After each Socratic exchange: mastery_node updates MasteryLedger asynchronously.
- If mastery_score hits all threshold conditions: cert_node generates Proof of Mastery (delivered next session).

## **4.4 Session Exit Flow**

- User closes workspace or triggers exit.
- Memory Node saves full State Snapshot (JSON + SQLite).
- System asks: 'Do you want a Lessons Learned summary for your private journal?'
- If yes: OllamaService generates summary in mentor's voice - what was accomplished, what was learned, which concepts changed status.
- Mastery Ledger update finalised and committed.

# **5\. Technical Stack**

| **Layer**          | **Technology**        | **Rationale**                                                                                                        |
| ------------------ | --------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Orchestration**  | LangGraph             | Stateful multi-agent graph. Required for session memory and node separation. Each node is independently replaceable. |
| **RAG Pipeline**   | LlamaIndex            | Best-in-class Agentic RAG. Handles multi-source ingestion, semantic chunking, retrieval from ChromaDB.               |
| **LLM Runtime**    | Ollama (local)        | Local inference ONLY. Private vault data and session data never leave the machine.                                   |
| **Base Model**     | llama3.2:3b           | Fits in 8 GB RAM. No corporate guardrails on tone. Use phi3:mini as fallback.                                        |
| **Embedding**      | nomic-embed-text      | Runs via Ollama locally. No external embedding API.                                                                  |
| **Vector DB**      | ChromaDB (local)      | Persistent local directory. Namespaced per persona. Never in-memory for production.                                  |
| **Relational DB**  | SQLite + aiosqlite    | Sessions, MasteryLedger, MasteryCertificates. Local, no server. Via SQLAlchemy async.                                |
| **Backend**        | FastAPI + Python 3.11 | Lightweight, async, integrates cleanly with LangGraph and LlamaIndex.                                                |
| **Transcription**  | Whisper (local, base) | Local video/audio to text. Offline. No data leakage. base or small model ONLY.                                       |
| **Scraping**       | Scrapy + Playwright   | Scrapy for static pages. Playwright for JS-rendered content (Twitter, LinkedIn).                                     |
| **Safety**         | DistilBERT (local)    | Guardian shadow classifier. Loaded lazily. Fast. Runs offline.                                                       |
| **Workspace Hook** | VS Code Extension     | Phase 2 addition. Monitors terminal errors, file saves, idle. Posts to /workspace/event.                             |
| **Frontend**       | React + Vite + TS     | SPA on localhost:5173. No cloud dependency.                                                                          |
| **Containers**     | Docker + compose      | Full dev environment in containers. Reproducible. Ollama in its own container.                                       |

## **5.1 Privacy Architecture Rules (Hard Requirements)**

- ZERO external API calls for inference - Ollama only. No OpenAI, Anthropic, Gemini, or any cloud LLM
- All vector databases run locally - ChromaDB in a local directory
- Private vault uploads encrypted at rest (AES-256)
- Session snapshots, Mastery Ledger, and Proof of Mastery certificates stored locally only
- Shadow classifier runs locally - no external moderation API
- evolution_db.json built from local fingerprint analysis only - no external AI service
- The ONLY permitted external network calls: (1) Playwright scraping during fingerprint ingestion, (2) yt-dlp for YouTube downloads. BOTH triggered only by explicit user action.

# **6\. Non-Functional Requirements**

| **ID**      | **Category**     | **Requirement**                                                                                                                                                       |
| ----------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-001     | Latency          | Socratic interruption prompts delivered within <2 seconds of detected deviation. ETM injection adds <300ms. Guardian classifier adds <500ms.                          |
| NFR-002     | Authenticity     | The persona must pass a Persona Turing Test: someone who knows the mentor should find the advice and tone recognizably consistent with the real person.               |
| NFR-003     | Explainability   | Every Socratic intervention at Level 2+ must cite a specific source in the Private Wisdom Vault. No hallucinated citations permitted.                                 |
| NFR-004     | Privacy          | Zero external data transmission for user-generated content, private vault data, mastery data, or certification content. Local inference is non-negotiable.            |
| NFR-005     | Persistence      | Session state and Mastery Ledger must survive application crashes. Auto-save every 60 seconds. Full snapshot on graceful exit.                                        |
| NFR-006     | Scalability      | Architecture must support a future Marketplace where Persona Seeds (soul profiles without vault data) can be shared. Mastery data always stays private.               |
| NFR-007     | Extensibility    | Each LangGraph node must be replaceable independently. Swapping the base LLM or vector DB requires changes only to the relevant node.                                 |
| **NFR-008** | Mastery Accuracy | \[v3\] mastery_score formula must be deterministic and auditable. The user must be able to see exactly WHY a concept has its current status. TDD is the formal audit. |
| **NFR-009** | Mastery Async    | \[v3\] mastery_node and cert_node must NEVER add latency to the user-facing response path. They run after the response is delivered.                                  |
| **NFR-010** | Cert Integrity   | \[v3\] Proof of Mastery certifications must not be issued unless ALL conditions in REQ-CERT-001 are met simultaneously. No partial certifications.                    |
| **NFR-011** | Superpowers      | \[v4\] Every phase must begin with git-worktrees + writing-plans. No production code before plan is approved.                                                         |
| **NFR-012** | TDD              | \[v4\] All 7 LangGraph nodes + all services + RAG retriever must be implemented test-first. No exceptions.                                                            |
| **NFR-013** | Context7         | \[v4\] No library API may be implemented from memory. Context7 MCP must be resolved for each external library before use.                                             |
| **NFR-014** | YAGNI            | \[v4\] No feature, abstraction, or optimisation is built unless required by an explicit REQ or NFR. YAGNI is law.                                                     |
| **NFR-015** | DRY              | \[v4\] No logic duplicated across nodes or services. Shared Python utilities → core/utils.py. Shared frontend logic → hooks/ or lib/.                                 |

# **7\. MVP Build Order - 5 Phases**

_BUILD IN THIS EXACT ORDER. Complete and test each phase before starting the next. Each phase ends with a verification checklist - all items must pass before the next phase begins._

## **Phase 1 - Core Engine + Docker (Weeks 1-4)**

Goal: User can chat with a persona. Session saves and resumes. Docker dev environment running. Sacred Space opening ritual (basic).

- Docker: docker-compose.yml running Ollama + backend + frontend
- Private Vault Ingestion (REQ-INGEST-005, 006) - PDF and video upload, local vector storage
- Persona System Prompt (REQ-PERSONA-001, 002) - Llama 3.2:3b + few-shot style transfer
- Session State Schema (REQ-MEMORY-002) - JSON + SQLite save/load
- Sacred Space Opening Ritual - basic: black screen → mentor name types → Enter to continue
- ResumeModal with contextual re-sync greeting
- All LangGraph nodes present - Modules 5, 6, 7 nodes are STUBS only in Phase 1

## **Phase 2 - Socratic Engine (Weeks 5-8)**

Goal: Socratic Ladder activates. VS Code extension sends workspace events.

- VS Code Extension: terminal error, file save, idle event posting (REQ-SOCRATIC-001)
- Full socratic_node without mastery context yet (REQ-SOCRATIC-003, levels 0-4)
- Deviation Threshold Engine (REQ-SOCRATIC-002, without MasteryLedger reading)
- Persona Dashboard sliders (REQ-PERSONA-003)
- Full ingest pipeline: rag/vault.py, rag/fingerprint.py, rag/retriever.py

## **Phase 3 - Mastery Tracking + ETM (Weeks 9-12) \[v3.0\]**

Goal: Cross-session mastery tracking is live. Ethical Time Machine proactively injects evolution context.

- MasteryLedger SQLite table and schema (REQ-MASTERY-001, 002)
- mastery_node: concept extraction + ledger update as FastAPI BackgroundTask (REQ-MASTERY-003)
- Mastery Map UI component (REQ-MASTERY-004)
- Mastery-aware Socratic Ladder - reads MasteryLedger for starting level (REQ-SOCRATIC-002 updated)
- evolution_db.json seeded during fingerprint ingestion (REQ-ETM-001)
- etm_node: proactive evolution injection (REQ-ETM-002)

## **Phase 4 - Proof of Mastery + Guardian Full (Weeks 13-16) \[v3.0\]**

Goal: Certifications are issued. Guardian shadow classifier is live. Real persona soul from fingerprint data.

- cert_node: certification trigger + in-character generation (REQ-CERT-001, 002)
- MasteryCertModal UI component (REQ-CERT-004)
- Certificate storage and PDF export (REQ-CERT-003)
- Guardian shadow classifier: full DistilBERT implementation (REQ-ETM-003)
- Full public fingerprint pipeline: YouTube, social media, linguistic profile extraction
- Gap-Fill Interview system (REQ-INGEST-007, 008)

## **Phase 5 - Sacred Space Full + Polish (Weeks 17-20)**

Goal: Full Sacred Space ritual. Friend Mode. Lessons Learned. Production hardening.

- Full Sacred Space opening animation (typewriter effect, workspace materialises from black)
- Focus Mode: dim effect - all UI outside chat dims to 15% opacity in Deep Dive mode
- Friend Mode: toggle, suspend Socratic + mastery, UI colour shift amber→blue
- Lessons Learned modal on session exit - includes concept status movements
- Auto-save every 60 seconds (frontend setInterval → POST /session/save)
- Error handling: Ollama offline banner, vault ingest failure recovery, guardian failure passthrough
- README.md with Docker quickstart + manual setup + first-run guide
- scripts/setup.sh and scripts/start-docker.sh finalised

_End of Document - PME SRS Final Version_
