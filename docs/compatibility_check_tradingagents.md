# TradingAgents Compatibility Check

**Date:** 20 November 2026
**Version checked:** TradingAgents 0.7.1, commit `9fa1196fffbcfd9de5146d2dd2869df84ab99838` (cloned to `vendor/TradingAgents`)
**Environment:** Python 3.12.6 virtual environment in `.venv`, Windows 11, RTX 3050 4 GB
**Question:** Can TradingAgents serve as the base for the four-condition evidence-verification experiment?

## Short answer

**Partly.** Use it as a library, not as the full pipeline. Its model-provider layer and LangGraph structure are useful and work. Its fixed agent pipeline, decision format, portfolio handling and data sources do not fit the paper, so those parts have to be ours.

## What was done

1. Cloned the repository and checked out the pinned commit.
2. Read the graph setup, portfolio, decision schemas, data router, config and LLM factory.
3. Installed it in a Python 3.12 venv. Python 3.14 was not tried; the package requires 3.11 or newer.
4. Ran its offline test suite: **1,407 passed, 6 skipped, 0 failed**, in 48 s. This includes a full end-to-end graph run with scripted models and no network.
5. Tried to fetch Egyptian prices from Yahoo Finance (`COMI.CA`, `ETEL.CA`, `TMGH.CA`, `ABUK.CA`, `EFID.CA`, `HRHO.CA`).

No real language-model call was made, so no API key or money was used.

## Findings

| Area | What the code does | Fits the paper? | What we need |
|---|---|---|---|
| Model providers | Anthropic, Google Gemini, Groq, OpenRouter, Ollama, OpenAI, DeepSeek and others, chosen by config. Quick and deep tiers can use different providers. | **Yes** | Develop on a free tier (Gemini, Groq, OpenRouter or local Ollama, which is already installed), then switch to Claude for the final runs. |
| Agent pipeline | Fixed: 4 analysts in parallel → bull/bear debate → research manager → trader → 3 risk debaters → portfolio manager. That is a dozen or more model calls per run. | **No** | Choosing one analyst still keeps the other agents, so there's no true single-agent baseline. We build our own small graphs: one single-agent graph and one multi-agent graph, using the same LangGraph tools. |
| Portfolio | `PortfolioContext` turns holdings into prompt text only. Quantity is signed, so short positions are allowed. Nothing is enforced. | **No** | Our own independent checker: no unowned sales, no overselling, cash reconciles, arithmetic is valid. |
| Decision output | Rating is Buy / Overweight / Hold / Underweight / Sell. Sizing is free text. There is no quantity, no "keep cash" and no "insufficient evidence". | **No** | Our own decision schema: action, number of shares, amount, cited evidence and figures not used. |
| Data sources | Yahoo, Alpha Vantage, SEC EDGAR, FRED, Polymarket, Reddit and StockTwits, all US-focused. No PDF reading. | **No** for EGX | Add our own source of frozen official disclosures. The router's `VENDOR_METHODS` table is a clean place to plug it in. |
| Yahoo for EGX | Not verified. Yahoo's client failed on this laptop with an SSL certificate error, though plain `curl` reaches Yahoo, so the problem is local. | Unknown | Not needed for the paper's main question; prices are secondary. Revisit only if price features are used. |
| Memory between runs | A memory log is on by default in `~/.tradingagents/memory/` and feeds past decisions to later runs. | Risky | Turn it off or give each run its own path, so conditions can't learn from each other. |
| Output language | `output_language` setting exists. | Partly | Arabic output is only a prompt instruction. It says nothing about reading Arabic or scanned documents. |
| License | Apache-2.0 | Yes | Keep the license and notices if we copy or change code. |

## Recommendation

Build a slim project of our own and import from TradingAgents only what fits:

- **Reuse:** the LLM client factory (provider switching), the LangGraph patterns, and the analyst prompts as reference text.
- **Write ourselves:** document reader, evidence store, single-agent and multi-agent graphs, verifier (one fix attempt, then flag), portfolio checker, decision schema, scorer.

This keeps conditions A–D comparable, because every condition gets the same data, tools, schema and checker and differs only in agent count and verifier. It also cuts model calls per run, which matters on free tiers.

## Still open

- Choice of free development model. Gemini free tier or Groq is the simplest start. Your 4 GB GPU only fits very small local models.
- The Yahoo SSL error on this laptop, if price data is ever needed. Likely antivirus or proxy certificate interception. Do not fix it by turning off certificate checks.
- Exact multi-agent topology for condition C/D: how many agents and which roles.
