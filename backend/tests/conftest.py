import os

# Tests import app.config (directly or transitively), which validates
# Settings at module-import time and requires OPENROUTER_API_KEY. Tests never
# make real OpenRouter calls, so a placeholder is enough — set before any
# test module imports app.config. Real runs get the real key from .env.
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-not-used")
