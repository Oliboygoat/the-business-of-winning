# AI Analyst: architecture and public release status

**Public release override:** the shipped interface is free-demo-only. It does not read API secrets, render a paid-mode selector, or call the experimental engine. `answer_ai()` always refuses and `build_client()` always raises, regardless of environment or credentials. The SDK is a test-only dependency. The sections below describe the earlier experimental architecture; they do not authorize or enable live requests.

## What works now

The fifth navigation section is **AI Analyst**, between Insights and Methodology. The permanent free demo runs entirely on the saved dataset. No API key, hosted model, embeddings, or paid service is needed. Click an example or enter a supported question about rankings, comparisons, team trends, consistency, annual models, Colorado sensitivity, or sources. Every result includes its seasons, payroll definition, limitations, direct source links, and expandable calculation records. Chat can be cleared or downloaded.

The demo is a small question router, not a language model. It recognizes documented patterns, including team names and year ranges; unsupported wording receives a helpful refusal rather than a guessed answer. It does not promise arbitrary conversational follow-ups. A range containing 2022 is blocked without the separate chat permission, even if the question text says permission is granted. Broad default demo trends use the five AP years. Single-season 2022 remains available with its TBC definition disclosed.

**Stage 1 was completed and verified before Stage 2 implementation:** 75 tests passed, including all 56 pre-existing checks. The gate was recorded in the private `audit/analyst_stage1.json`; that historical artifact and pre-feature commit `90a5277` are not included in the fresh public history. Current candidate checks are described in `VERIFICATION.md`.

## What is implemented but only mock-tested

The OpenAI integration uses the official Python SDK and Responses API, pinned to `gpt-5.4-mini-2026-03-17`. It uses strict function schemas and a short tool loop. There is no arbitrary Python, SQL, shell, code interpreter, browser, file tool, or model-selected network destination.

The model interprets a question, chooses `analyze_mlb` queries, and reads their structured results. At the end it calls `present_answer` to select result IDs and a vetted interpretation. Python renders the corresponding numerical narrative. The model's free-form text is never displayed, and it cannot substitute new numerical prose or citations. This is intentionally constrained synthesis rather than an unrestricted chatbot: it can choose and combine at most two supported analyses per turn. It may still misunderstand a question or pick an unhelpful analysis. Honest numbers alone do not prove that an answer addresses the user's intent.

Up to four recent exchanges and their successful query contexts are supplied for pronouns and follow-ups. Older context is not retained in API inputs. Provider-side response storage is disabled (`store=False`); this does **not** mean OpenAI has zero retention under all policies. No remote conversation ID is used. Browser-session history is limited to twelve questions; the usage ledger stores only time, a hashed access identity, and reservations, not chat text or credentials.

Tests use both fake response objects and the real SDK against an **in-memory mock HTTP transport**, exercising serialization, tool-result round trips, and response parsing without a network connection. This verifies protocol wiring and deterministic results. It does not verify the live model's question interpretation, account/model availability, latency, actual token use, rate limits, or cost. No paid request has been made.

## How to explain the architecture in an interview

- `analyst/tools.py` is a read-only API over the existing verified Python functions. `Query` is a small typed description of an analysis; it cannot contain executable instructions.
- `analyst/demo.py` converts a limited set of question patterns into that same query structure.
- `analyst/openai_service.py` lets a language model select queries and arrange results. All tool names, fields, IDs, seasons, result references, and source permissions are checked again in Python; the schema is not the security boundary by itself.
- `analyst/security.py` checks server enablement and private owner access, then reserves a conservative allowance in SQLite **before** a provider request.
- `analyst/ui.py` provides the chat, examples, history, source panels, permission control, and useful failure states.

The source data, `analytics.py`, and `multi_analytics.py` are unchanged. Annual regressions still use all thirty teams; no pooled franchise-year model is introduced. March 2026 CPI adjustments apply to monetary comparisons and trends, while annual model tables retain nominal-dollar definitions. Each year's residual benchmark remains unchanged. A low payroll per win is not profitability or necessarily competitive success. Correlation is not causation, and historical consistency is not a forecast or evidence of management skill.

## Credentials and public release

No secrets are needed. Leave Streamlit Community Cloud's Secrets field empty. Environment variables, owner tokens, and legacy enablement flags cannot activate paid AI in this branch. The old live SDK constructor has been removed; the public service function refuses all calls. The experimental orchestrator requires an explicitly injected client and is retained for mocked tests only. It has no connection to the UI.

A future private/live release would need an intentional code change, separate review and explicit owner approval. Setting a flag or adding an API key is insufficient. Never put credentials in chat, a URL, a screenshot or a committed file. `.env` variants, real Streamlit secrets, runtime files and local usage databases remain ignored.

## Historical experimental controls and cost estimates (not active in public mode)

The earlier private client used a fixed API host/model, no automatic retries, and a 25-second timeout. That live client constructor is absent from this public release. Each turn allows at most three model calls, two analytical queries, 1,200 user characters, 24,000 serialized input bytes per call, and 1,000 output tokens per call. Overlarge, incomplete, invalid or unverified responses fail closed.

A SQLite transaction reserves each paid turn before HTTP. Limits survive a conversation clear, new browser session, and application restart when the ledger is persistent. Reservations are not refunded after failures because a timed-out call may still have been billed. Default controls are:

- Five access attempts per minute across the instance.
- Five turns per hour per owner credential (hashed; not a resettable browser ID).
- Twenty turns per UTC day across the instance.
- One million conservatively reserved tokens and one dollar of reserved allowance per UTC day across the instance. The lowest applicable limit wins; token reservations normally limit this to ten turns per day.
- A reservation of 93,000 tokens and **$0.081 per turn**, allowing for three calls with conservative input overhead and maximum output. This is a safety allowance, not an observed bill or a provider-enforced hard spend cap.

The official [model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini) lists standard text prices of **$0.75 per million input tokens** and **$4.50 per million output tokens**, checked during implementation. For example, 10,000 total input tokens and 1,500 total output tokens across a turn's calls would cost about **$0.01425** at those rates. Cached-input discounts are not assumed. This is illustrative; actual usage is unmeasured. Recheck pricing and eligibility before approval, and use provider project limits alongside application limits. Regional processing or pricing changes can alter charges.

## Deployment boundary: public free demo only

The public portfolio deployment exposes the **free demo only**. The earlier owner-token gate was intended for private testing and is no longer rendered. Do not publish an access token or enable anonymous paid requests.

Before any approved public paid rollout, add real user authentication, per-user quotas, an edge/gateway rate limiter, abuse monitoring, an owner kill switch, TLS, and persistent shared quota storage appropriate to the hosting topology. SQLite supports one host with concurrent processes on the same persistent local disk; it does not coordinate separate containers or replicas. Ephemeral disks reset limits and must not host enabled paid mode. This release intentionally does not claim a completed public paid service.

## Validation and launch

```bash
source .venv/bin/activate
python -m pytest -q
streamlit run app.py --server.address 127.0.0.1
```

Open `http://127.0.0.1:8501/`, choose **AI Analyst**, and leave **Free demo** selected. No paid API mode is offered in the public interface. Desktop browser checks cover examples, sources, unsupported questions, the 2022 permission, and the locked mode; real mobile and assistive-technology testing remain outstanding.

Official integration references: [Responses API function calling](https://developers.openai.com/api/docs/guides/function-calling) and [model capabilities and pricing](https://developers.openai.com/api/docs/models/gpt-5.4-mini). Source definitions and unresolved AP/TBC accounting differences remain in `MULTISEASON_SOURCES.md` and the dashboard's Methodology.
