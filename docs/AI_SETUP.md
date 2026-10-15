# AI configuration

The app runs immediately in `LLM_PROVIDER=demo`. That mode is deterministic parsing and is labeled; it is NOT an LLM. Switch to one of the configurations below for real model inference. Groq was exercised during developer testing; live Ollama inference was not verified for this release. Automated adapter tests use simulated responses.

## Option A — local Ollama

Use the Ollama installation/model already available on your machine, or install from https://ollama.com. List installed models with `ollama list`. If needed, pull a model that supports JSON output and fits your laptop. Model latency and quality must be measured on the target machine; GPU availability is not required by NextStep itself.

Edit `.env`:

```dotenv
LLM_PROVIDER=ollama
LLM_BASE_URL=http://127.0.0.1:11434
LLM_MODEL=YOUR_EXACT_INSTALLED_MODEL_NAME
LLM_API_KEY=
LLM_TIMEOUT=45
```

Replace the placeholder; do not copy it literally. Keep Ollama running, restart NextStep, and try the prompts below. The adapter calls native `/api/chat`, supplies the JSON schema through `format`, disables streaming and uses temperature zero.

For Docker Desktop, the host Ollama service is normally reached using `http://host.docker.internal:11434`; verify reachability and the Ollama listening configuration. Do not expose Ollama publicly.

## Option B — compatible cloud API (for example Groq)

Use a model in your account that supports chat completion and JSON-object output. In `.env`:

```dotenv
LLM_PROVIDER=compatible
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=YOUR_CURRENT_JSON_CAPABLE_MODEL_ID
LLM_API_KEY=YOUR_PRIVATE_API_KEY
LLM_TIMEOUT=30
```

This app appends `/chat/completions` to the base URL. It uses `response_format={"type":"json_object"}`, temperature zero and a bounded output length. API compatibility varies by provider/model; if the provider rejects these fields, choose a supported model or adapt `model_plan` after consulting that provider's official docs. Do not silently remove schema validation.

A ChatGPT subscription is not an API key or an API usage allowance. NextStep has no dependency on an ongoing assistant subscription. Provider costs and limits are your account's responsibility. No cloud provider is required for the rule-based demo or local Ollama path.

## What the AI actually does

It chooses one bounded action per message: update preferences, retrieve options, select an option, resume, or request clarification. Pydantic validates the plan; service functions enforce current revision, ownership and availability. Assistant replies are composed from service results. This deliberate separation keeps booking claims grounded.

The model receives current preferences, available options and the last eight conversation messages. With a cloud model, that content leaves the server for your selected provider. Use fictional data in demos and disclose this to real users before collecting personal data.

The model never receives session tokens or API credentials. It has no booking-confirmation action, unrestricted Python execution, browsing tool, payment access or arbitrary URL access.

## Live acceptance prompts

1. `My fan is rattling in Central. Find a visit tomorrow afternoon under 500 rupees.`
2. `Actually, make it Friday morning and keep the visit fee under 400.`
3. `Choose the first option.`
4. `I will finish later.`
5. Resume using the UI, then explicitly confirm.

Check the task detail panel against each prompt. If a model misunderstands, correct using Edit details and record the issue. Cloud errors do not trigger hidden rule-based fallback; the UI reports the failure.

## Source references

- https://docs.ollama.com/api/chat
- https://console.groq.com/docs/openai
- Check your selected provider's current model and pricing documentation before choosing a model.
