# Chapter 8: Set Up an AI Provider

[Home](../README.md) · **Chapter 8 of 10**

Configure a provider that supports the OpenAI Responses API. You will implement
the integration in the next chapter.

## Before You Begin

Merge the logging pull request and confirm your working tree is clean, then
create the Task 4 branch:

```bash
git status
git checkout main &&
git pull --ff-only origin main &&
git checkout -b feature/ai-analysis
```

Keep this branch for Chapters 8 and 9. Open the `task:analysis` pull request
after implementing the integration in the next chapter.

## Choose a Provider

| Provider | `OPENAI_BASE_URL` | `OPENAI_MODEL` |
|----------|-------------------|----------------|
| Microsoft Foundry Models | `https://<resource>.services.ai.azure.com/openai/v1/` | Your deployment name |
| OpenAI | `https://api.openai.com/v1` | A model available to your account |

For Microsoft Foundry, create a model deployment and copy its endpoint, key,
and deployment name from the portal. The selected provider and model must
support the Responses API.

## Configure `.env`

Replace the three placeholders:

```text
OPENAI_API_KEY=<your provider API key>
OPENAI_BASE_URL=<your Responses API-compatible v1 endpoint>
OPENAI_MODEL=<your model ID or deployment name>
```

Do not commit these values or add them to GitHub Actions. CI uses mocked HTTP
transport and does not need provider credentials.

Restart the API after changing `.env`; settings are loaded and cached when the
application starts.

## Protect Your Data

Use only synthetic, non-sensitive journal entries with the provider. Do not
send personal journal content, credentials, or other secrets.

You will confirm the credentials after implementing the service in Chapter 9.

---

[← Previous: Logging](07-logging.md) ·
[Next: Build AI-powered analysis →](09-ai-analysis.md)
