# RealAI Frontend

A professional Next.js 15 chat interface for the [RealAI](https://realai-qz3b.onrender.com) backend.

## Features

- 💬 **Full chat UI** — streaming-style responses, markdown rendering, code blocks
- 🔄 **Conversation history** — persisted in localStorage, grouped by date
- 🧠 **Model selector** — RealAI 2.0, GPT-4o, Claude 3.5 Sonnet, Mistral Large, and more
- ⚙️ **Settings drawer** — system prompt, temperature slider, max tokens, optional API key
- 📱 **Responsive** — collapsible sidebar, works on mobile
- 🌑 **Dark mode** — slate/indigo design system, zero flash

## Getting Started

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.local.example .env.local
# Edit .env.local and set NEXT_PUBLIC_REALAI_API_BASE if needed

# 3. Run locally
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deploy to Vercel

1. Create a **new** Vercel project and point it at the `realai-frontend` subdirectory of this repository.
2. Add the following environment variables in the Vercel dashboard:

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_REALAI_API_BASE` | `https://realai-qz3b.onrender.com` |
| `REALAI_API_KEY` | *(your backend API key, if required — stored server-side only)* |

3. Deploy. The proxy route at `/api/chat` forwards requests to the Render backend, so API keys never reach the browser.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_REALAI_API_BASE` | Yes | Base URL of the RealAI backend |
| `REALAI_API_KEY` | No | Server-side API key forwarded to the backend |

## Architecture

```
Browser → /api/chat (Next.js proxy) → https://realai-qz3b.onrender.com/v1/chat/completions
```

The proxy avoids CORS issues and keeps the API key server-side (never exposed in browser network traffic).
