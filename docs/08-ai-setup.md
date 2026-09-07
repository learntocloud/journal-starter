# Chapter 8: Set Up an AI Provider

[Home](../README.md) · **Chapter 8 of 10**

In this chapter, you will choose an AI provider and configure the settings the
application needs to connect to it. You will implement the integration in the
next chapter.

## 1. Prepare Your Branch

1. Make sure your logging pull request is merged, then check your working tree:

   ```bash
   git status
   ```

   It should be clean before you continue.

2. Switch to `main`:

   ```bash
   git checkout main
   ```

3. Pull the latest changes:

   ```bash
   git pull origin main
   ```

4. Create the branch for the AI integration:

   ```bash
   git checkout -b feature/ai-analysis
   ```

   Keep this branch for both Chapters 8 and 9. Do not open a pull request yet.

## 2. Choose a Provider

1. Choose a provider and model that support the OpenAI Responses API.

   An AI provider hosts the model that processes your requests. The Responses
   API is the interface this project uses to send journal text to the model and
   receive its analysis. Supporting other OpenAI interfaces does not necessarily
   mean a provider supports this one.

   | Provider | `OPENAI_BASE_URL` | `OPENAI_MODEL` |
   |----------|-------------------|----------------|
   | Microsoft Foundry Models | `https://<resource>.services.ai.azure.com/openai/v1/` | Your deployment name |
   | OpenAI | `https://api.openai.com/v1` | A model available to your account |

2. In your provider's portal, choose a supported model. For Microsoft Foundry,
   create a model deployment and note its deployment name. For OpenAI, note the
   model ID available to your account.

   Check the provider's pricing and your account's access before proceeding.
   The required live request in the next chapter may incur a charge.

3. Locate or create an API key and obtain the endpoint for your selected provider.
   For Microsoft Foundry, copy the endpoint and key from the portal.

   The endpoint is the address the application sends requests to. The API key
   authenticates those requests. The model ID or deployment name selects the
   model that will process them.

## 3. Configure the Application

1. Open `.env` in VS Code and find `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and
   `OPENAI_MODEL`.

2. Replace the three placeholders with your provider's values:

   ```text
   OPENAI_API_KEY=<your provider API key>
   OPENAI_BASE_URL=<your Responses API-compatible v1 endpoint>
   OPENAI_MODEL=<your model ID or deployment name>
   ```

   Replace the angle brackets and the text inside them. Leave the database
   settings unchanged.

3. Save `.env`. Do not commit the values or add them to GitHub Actions.

   CI uses a mocked HTTP transport, which supplies test responses instead of
   contacting the provider. It does not need real provider credentials.

4. If the API is running, stop it with `Ctrl+C` in its terminal.

   Settings are loaded and cached when the application starts. Saving `.env`
   does not replace the settings in an already running process.

5. Start the API with the updated settings:

   ```bash
   uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Successful startup does not confirm that the provider credentials work.
   You will make a live request after implementing the service.

## Before You Continue

Your provider settings should be saved locally, and you should still be on
`feature/ai-analysis`. Continue on this branch in Chapter 9; the `task:analysis`
pull request comes after the implementation and live verification.

---

[← Previous: Logging](07-logging.md) ·
[Next: Build AI-powered analysis →](09-ai-analysis.md)
