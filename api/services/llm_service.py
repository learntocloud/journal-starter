import os
import json
from openai import AsyncOpenAI
from typing import Dict, Any

# Initialisierung des Clients für GitHub Models (Phase 3 Standard)
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://models.inference.ai.azure.com"),
)

async def analyze_journal_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Sendet den Eintrag an die KI und gibt Sentiment, Summary und Topics zurück."""
    prompt = f"""
    Analysiere diesen Tagebucheintrag und gib ein JSON-Objekt zurück mit:
    - sentiment: (string)
    - summary: (2 Sätze Zusammenfassung)
    - topics: (Liste von 3 Themen)
    
    Eintrag: {entry}
    """
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "sentiment": "error",
            "summary": f"Fehler bei der KI-Analyse: {str(e)}",
            "topics": []
        }
