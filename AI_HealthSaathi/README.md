# AI HealthSaathi

Multilingual AI health-information and prescription-understanding assistant.

## Features
- Health questions in Indian regional languages
- Voice questions
- Medicine/prescription image analysis
- English prescription -> regional-language explanation
- Basic RAG knowledge file
- Safety-first behavior

## Setup

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run:
   pip install -r requirements.txt
4. Copy `.env.example` to `.env`.
5. Add your Gemini API key:
   GEMINI_API_KEY=YOUR_KEY
6. Run:
   streamlit run app.py

## Important
This is a hackathon MVP for educational/general information. It does not diagnose, prescribe, or change a doctor's medication instructions. Unclear information should be verified with a doctor or pharmacist.

Never upload your real `.env` or API key to GitHub.
