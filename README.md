# Multimodal Construction Intelligence Platform

AI decision-support app for construction: PPE/safety audit from site photos, crack diagnostics,
cost planning and valuation in INR, weather-aware advisory, and a construction Q&A assistant.

## Tech stack
Python 3.9+, Streamlit, Google Gemini (multimodal), Pillow, strict JSON data contracts.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py
Paste a Gemini API key (https://aistudio.google.com) in the sidebar, or use demo mode without one.

## Features
- Site Safety & PPE audit (score, PPE checklist, hazards, JSON export)
- Crack diagnostics (type, width, severity, causes, repairs)
- Planning & valuation (budget, capex, asset value, cement/steel estimates)
- Weather advisory and multi-turn construction assistant

## Known limitations
AI output is advisory, not a certified inspection or valuation. Cost rates are simplified heuristics.
