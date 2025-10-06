# Manufacturing Training Studio — Streamlit App

Created: 2025-10-04T18:36:36.595873Z

Generate manufacturing training assets (syllabi, video scripts, storyboards, narration, quizzes) from a structured KB, with optional LLM.

## Run locally
```bash
cd manufacturing-training-app
pip install -r requirements.txt
export OPENAI_API_KEY=YOUR_KEY   # optional for LLM
streamlit run app.py
```
Folders: `kb/`, `personas/`, `generators/prompts/`, `outputs/`.
