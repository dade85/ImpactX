# -*- coding: utf-8 -*-
"""
Created on Sat Oct 04 17:02:26 2025

@author: DavidAdewunmi
"""

# app.py — ImpactX Manufacturing Training Studio
# Multilingual • Curriculum-aware • Instant Video • Bulletproof Rendering
# + Sidebar "Dashboard Guide" (Features + KB Explorer)
# + 📚 Knowledge Base tab
# + LLM Q&A integrated on the main page

import os, sys, json, re, tempfile, shutil, subprocess
from typing import Dict, List
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ImpactX — Circular Innovation Program", layout="wide")

# =========================
# Branding & Theme
# =========================
LOGO_PATH = "C:/Users/DavidAdewunmi/Downloads/SecurityDashboard/manufacturing-training-app/ImpactX.png"          # place your logo file in project root
PRIMARY_BG = "#0d0221"
ACCENT = "#ff4d4f"

CUSTOM_CSS = f"""
<style>
    .block-container {{ padding-top: 1.2rem; }}
    header {{ visibility: hidden; }}
    .impact-header {{
        display:flex; align-items:center; gap:10px; padding:10px 16px;
        background:{PRIMARY_BG}; border-radius:12px; margin-bottom:12px;
    }}
    .impact-title {{ color:white; font-weight:800; font-size:1.25rem; letter-spacing:1px; }}
    .impact-badge {{ color:#fff; opacity:.85; font-size:.9rem }}
    .card {{
        border-radius:16px; border:1px solid rgba(0,0,0,.06);
        background: #fff; padding:16px 16px; box-shadow: 0 1px 3px rgba(0,0,0,.06);
    }}
    .stButton>button {{ border-radius:12px; height:48px; font-weight:700 }}
    .primary>button {{ background:{ACCENT}; color:#fff }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================
# Env bootstrap (FFmpeg + deps)
# =========================
def ensure_ffmpeg():
    try:
        import imageio_ffmpeg, os
        p = imageio_ffmpeg.get_ffmpeg_exe()
        if not os.path.exists(p): raise FileNotFoundError
        print("🎬 FFmpeg:", p)
    except Exception:
        st.write("Installing FFmpeg backend…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "imageio[ffmpeg]", "--quiet"])
        import imageio_ffmpeg
        st.write("FFmpeg ready:", imageio_ffmpeg.get_ffmpeg_exe())
ensure_ffmpeg()

def ensure_deps():
    pkgs = ["moviepy", "pillow", "pyttsx3", "imageio", "imageio-ffmpeg", "openai"]
    for p in pkgs:
        try: __import__(p.split("-")[0])
        except Exception:
            st.write(f"Installing {p}…")
            subprocess.check_call([sys.executable, "-m", "pip", "install", p, "--quiet"])
ensure_deps()

import pyttsx3
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from openai import OpenAI

# =========================
# Paths
# =========================
BASE = os.path.dirname(__file__)
KB_DIR = os.path.join(BASE, "kb")
PERSONA_DIR = os.path.join(BASE, "personas")
OUT_DIR = os.path.join(BASE, "outputs")
PREFS_PATH = os.path.join(OUT_DIR, "user_prefs.json")
os.makedirs(OUT_DIR, exist_ok=True)

# =========================
# Utils: load/save
# =========================
def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_personas():
    data = {}
    if os.path.exists(PERSONA_DIR):
        for f in os.listdir(PERSONA_DIR):
            if f.endswith(".json"):
                data[f.replace(".json","")] = load_json(os.path.join(PERSONA_DIR, f))
    return data

# ---------- Built-in fallback curricula ----------
def default_curricula() -> list:
    return [
        {
            "id":"LOTO-FOUNDATION",
            "title":"Lockout/Tagout (LOTO) Foundation",
            "target_roles":["Operators","Maintenance"],
            "duration_minutes":35,
            "objectives":["Identify energy sources","Apply/verify lock & tag","Restore safely"],
            "modules":[
                {"title":"Why LOTO matters","topics":["OSHA overview","Injury case studies"]},
                {"title":"The 6 core steps","topics":["Notify","Shutdown","Isolate","Lock/Tag","Verify zero energy","Return to service"]},
                {"title":"Hands-on verification","topics":["Try-start test","Gauge bleed-off","Stored energy check"]}
            ],
            "assessment":{"type":"quiz","items":8},
            "practical":{"type":"demo","rubric":["Identifies sources","Applies lock","Verifies"]},
            "standards_refs":["OSHA 1910.147"]
        },
        {
            "id":"FORKLIFT-SAFE",
            "title":"Forklift Safety & Operation",
            "target_roles":["Material Handling"],
            "duration_minutes":40,
            "objectives":["Pre-shift inspection","Load capacity & stability","Safe driving"],
            "modules":[
                {"title":"Pre-use checks","topics":["Tires","Mast chain","Hydraulics","Horn/lights"]},
                {"title":"Operating zones","topics":["Pedestrian right-of-way","Speed","Visibility"]},
                {"title":"Loading & stacking","topics":["CG triangle","Ramps","Dock edges"]}
            ],
            "assessment":{"type":"quiz","items":10},
            "practical":{"type":"route","rubric":["Inspection","Maneuvering","Load/unload"]},
            "standards_refs":["OSHA 1910.178"]
        },
        {
            "id":"CNC-BASICS",
            "title":"CNC Operator Basics",
            "target_roles":["CNC Operators"],
            "duration_minutes":45,
            "objectives":["Workholding & tooling","Program loading & dry-run","Inspection & alarms"],
            "modules":[
                {"title":"PPE & guards","topics":["Door interlocks","Chip shields"]},
                {"title":"Setup & offsets","topics":["Work zero","Tool length","Touch-off"]},
                {"title":"Running safely","topics":["Single-block","Feed hold","Alarm response"]}
            ],
            "assessment":{"type":"quiz","items":12},
            "practical":{"type":"run","rubric":["Setup","Dry-run","Measure parts"]},
            "standards_refs":["ISO 23125"]
        },
        {
            "id":"LEAN-5S",
            "title":"5S & Lean Foundations",
            "target_roles":["All Staff"],
            "duration_minutes":30,
            "objectives":["Recognize wastes","Apply 5S","Sustain improvements"],
            "modules":[
                {"title":"The 5S cycle","topics":["Sort","Set","Shine","Standardize","Sustain"]},
                {"title":"Visual management","topics":["Shadow boards","Labels","Kanban"]},
                {"title":"Safety linkage","topics":["Trip hazards","Spill control","Fire access"]}
            ],
            "assessment":{"type":"quiz","items":7},
            "practical":{"type":"gemba","rubric":["Before/After photos","Checklist score"]},
            "standards_refs":[]
        },
        {
            "id":"FIRE-SAFETY",
            "title":"Workplace Fire Safety",
            "target_roles":["All Staff"],
            "duration_minutes":25,
            "objectives":["Identify fire classes","Use PASS","Evacuation routes"],
            "modules":[
                {"title":"Classes & extinguishers","topics":["A/B/C/D/K","Compatibility"]},
                {"title":"PASS drill","topics":["Pull","Aim","Squeeze","Sweep"]},
                {"title":"Evac & muster","topics":["Routes","Wardens","Headcount"]}]
            ,
            "assessment":{"type":"quiz","items":6},
            "practical":{"type":"drill","rubric":["Locate extinguisher","PASS demo","Report out"]},
            "standards_refs":["NFPA 10"]
        }
    ]

# =========================
# Knowledge Base (self-seeding curricula)
# =========================
def load_kb():
    os.makedirs(KB_DIR, exist_ok=True)
    kb = {
        "machines": load_json(os.path.join(KB_DIR, "machines.json"), {"items": []}),
        "hazards": load_json(os.path.join(KB_DIR, "hazards.json"), {"examples": []}),
        "standards": load_json(os.path.join(KB_DIR, "standards.json"), {"standards": []}),
        "sops": load_json(os.path.join(KB_DIR, "sops.json"), {"items": []}),
    }
    # robust curricula load + auto-seed
    cur_path = os.path.join(KB_DIR, "curricula.json")
    cur_file = load_json(cur_path, None)
    cur_list = []
    if isinstance(cur_file, dict) and isinstance(cur_file.get("curricula"), list) and cur_file["curricula"]:
        cur_list = cur_file["curricula"]
    else:
        cur_list = default_curricula()
        save_json(cur_path, {"curricula": cur_list})
    kb["curricula"] = cur_list
    return kb

# ===== KB visualization helpers =====
def kb_summary(kb: dict) -> dict:
    return {
        "machines": len(kb.get("machines", {}).get("items", [])),
        "hazards": len(kb.get("hazards", {}).get("examples", [])),
        "standards": len(kb.get("standards", {}).get("standards", [])),
        "sops": len(kb.get("sops", {}).get("items", [])),
        "curricula": len(kb.get("curricula", [])),
    }

def kb_as_dataframe(kb: dict, section: str) -> pd.DataFrame:
    if section == "Machines":
        rows = kb.get("machines", {}).get("items", [])
        return pd.json_normalize(rows)
    if section == "Hazards":
        rows = kb.get("hazards", {}).get("examples", [])
        return pd.json_normalize(rows)
    if section == "Standards":
        rows = kb.get("standards", {}).get("standards", [])
        return pd.json_normalize(rows)
    if section == "SOPs":
        rows = kb.get("sops", {}).get("items", [])
        return pd.json_normalize(rows)
    if section == "Curricula":
        rows = kb.get("curricula", [])
        return pd.json_normalize(rows)
    return pd.DataFrame()

# =========================
# Heuristics
# =========================
def heuristic_storyboard():
    return pd.DataFrame([
        {"Frame":1,"Visual":"Intro / Goals","On-screen":"What you will learn"},
        {"Frame":2,"Visual":"Key controls","On-screen":"Do the right checks"},
        {"Frame":3,"Visual":"Practice","On-screen":"Apply safely on the floor"}
    ])

def heuristic_audio():
    return ("Welcome. In this module you will learn critical safety steps and how to "
            "apply them in real operations. Stay alert and follow each control exactly.")

# =========================
# Preferences
# =========================
def load_prefs():
    return load_json(PREFS_PATH, {"language":"en", "last_curriculum":"", "pattern_hint":""})
def save_prefs(p): save_json(PREFS_PATH, p)

# =========================
# LLM helpers
# =========================
def call_llm(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        return "No API key set."
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You design concise, standards-aligned manufacturing training."},
                {"role":"user","content":prompt}
            ],
            temperature=0.35,
            max_tokens=1800,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"LLM call failed: {e}"

def extract_json_from_text(text: str) -> dict:
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        candidate = fence.group(1).strip()
        for attempt in (candidate, candidate.replace("'", '"')):
            try: return json.loads(attempt)
            except Exception: pass
    brace = re.search(r"\{[\s\S]*\}", text)
    if brace:
        snip = brace.group(0)
        for attempt in (snip, snip.replace("'", '"')):
            try: return json.loads(attempt)
            except Exception: pass
    return {}

# =========================
# Renderer (MoviePy -> silent fallback)
# =========================
def render_video_bulletproof(storyboard_rows, outfile, narration_text=None, persona_lang="en", rate_wpm=180, voice_id=None):
    import numpy as np, imageio, tempfile, shutil
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    from PIL import Image, ImageDraw

    tmp = tempfile.mkdtemp(prefix="impactx_")
    width, height = 960, 540
    slides=[]
    try:
        # Slides
        for i, f in enumerate(storyboard_rows or [{"Visual":"Training Module","On-screen":"(empty)"}], 1):
            im = Image.new("RGB",(width,height),(245,247,250))
            d = ImageDraw.Draw(im)
            d.text((40,36), f"Frame {i}", fill=(0,0,0))
            d.text((40,100), f"Visual: {f.get('Visual','')}", fill=(30,30,30))
            d.text((40,160), f"Text: {f.get('On-screen','')}", fill=(50,50,50))
            p = os.path.join(tmp, f"slide_{i:02d}.png")
            im.save(p); slides.append(p)

        # TTS + MoviePy
        audio=None; aud_dur=None
        if narration_text:
            try:
                eng = pyttsx3.init()
                eng.setProperty("rate", rate_wpm)
                if voice_id: 
                    try: eng.setProperty("voice", voice_id)
                    except: pass
                wav = os.path.join(tmp,"nar.wav")
                eng.save_to_file(narration_text, wav); eng.runAndWait()
                audio = AudioFileClip(wav)
                aud_dur = getattr(audio, "duration", None)
            except Exception as e:
                print("[TTS failed]", e); audio=None

        try:
            per = (aud_dur if aud_dur else 2.5*len(slides)) / max(1,len(slides))
            clips=[ImageClip(s).set_duration(per) for s in slides]
            video=concatenate_videoclips(clips, method="compose")
            if audio is not None:
                try: video = video.set_audio(audio)
                except: pass
            video.write_videofile(
                outfile, fps=15, codec="libx264", audio_codec="aac",
                threads=2, ffmpeg_params=["-preset","ultrafast"],
                verbose=False, logger=None
            )
            return outfile
        except Exception as e:
            print("[MoviePy failed; silent fallback]", e)

        # Silent fallback
        writer=imageio.get_writer(outfile, fps=15, macro_block_size=None)
        for s in slides:
            img = Image.open(s).convert("RGB")
            writer.append_data(np.array(img))
        writer.close()
        return outfile
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# =========================
# UI — Sidebar (branding + prefs + Dashboard Guide)
# =========================
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=160)
    st.markdown("### ImpactX Circular Innovation Program")

    prefs = load_prefs()
    ui_lang = st.selectbox("🌐 Preferred Language", ["en","nl","fr","de","es"],
                           index=["en","nl","fr","de","es"].index(prefs.get("language","en")))
    pattern_hint = st.text_input("🧠 Pattern Hint (optional)", prefs.get("pattern_hint",""),
                                 help="E.g., 'Short modules, frequent quizzes'")
    if st.button("Save Preferences"):
        prefs.update({"language": ui_lang, "pattern_hint": pattern_hint})
        save_prefs(prefs)
        st.success("Preferences saved")

    # ---------- Dashboard Guide (Features + KB Explorer) ----------
    st.markdown("---")
    st.markdown("### 📘 Dashboard Guide")
    guide_choice = st.selectbox(
        "What would you like to see?",
        ["— Select —", "Features Overview", "Knowledge Base Explorer"],
        help="Explore what this app can do and browse the underlying knowledge base."
    )

    kb_local = load_kb()
    if guide_choice == "Features Overview":
        st.markdown(
            """
**ImpactX Training Studio — Features**

- **Curriculum-aware generation**  
  Pick from real training curricula (LOTO, Forklift, CNC Basics, 5S/Lean, Fire Safety).

- **Dynamic Mode**  
  The AI adapts to your **language** and **preferred pattern** (tone, structure, length).

- **Instant Video + Audio**  
  LLM → narration + storyboard → TTS → MP4; auto-plays in the app.  
  *If TTS is unavailable, the app still renders a silent MP4.*

- **Branding & UX**  
  Clean, professional UI with your ImpactX logo and theme.

- **Resilient Pipeline**  
  Automatic FFmpeg setup; MoviePy with a silent fallback via `imageio` to guarantee output.

- **Q&A Chat**  
  Ask the knowledge base questions (machines, SOPs, hazards, standards, curricula).

- **Heuristic Test Render**  
  One-click 3-slide test to confirm your video stack.

- **Preferences**  
  Language + pattern hints are saved and reused.
            """
        )
    elif guide_choice == "Knowledge Base Explorer":
        # quick counts
        counts = kb_summary(kb_local)
        st.caption("Quick counts")
        c1, c2, c3 = st.columns(3)
        c1.metric("Machines", counts["machines"])
        c2.metric("Hazards", counts["hazards"])
        c3.metric("Standards", counts["standards"])
        c4, c5 = st.columns(2)
        c4.metric("SOPs", counts["sops"])
        c5.metric("Curricula", counts["curricula"])

        st.markdown("View a section:")
        section = st.selectbox("KB Section", ["Machines", "Hazards", "Standards", "SOPs", "Curricula"])
        df = kb_as_dataframe(kb_local, section)
        if df.empty:
            st.info("No records found in this section.")
        else:
            st.dataframe(df, use_container_width=True)

            with st.expander("Quick visualizations", expanded=False):
                cat_cols = [c for c in df.columns if df[c].dtype == "object"]
                if cat_cols:
                    vc_col = st.selectbox("Column to summarize", cat_cols, index=0, key="kbexp_vc_col")
                    vc = df[vc_col].astype(str).value_counts().head(12)
                    st.bar_chart(vc)
                else:
                    st.caption("No categorical columns available for a quick chart.")

            st.download_button(
                "⬇ Download this section as JSON",
                data=df.to_json(orient="records"),
                file_name=f"kb_{section.lower()}.json",
                mime="application/json",
                use_container_width=True
            )

# =========================
# UI — Main
# =========================
kb = load_kb()
personas = load_personas()

# Tabs: keep KB tab; integrate Q&A on main tab
tab_render, tab_kb = st.tabs(["🎬 Instant Training Video", "📚 Knowledge Base"])

# ------------------ Instant Auto Video (Main Page)
with tab_render:
    st.markdown("## 🎓 Choose a Training Curriculum")
    cols = st.columns(3)
    curricula = kb.get("curricula", [])
    curr_titles = [f"{c['title']} ({c['duration_minutes']} min)" for c in curricula] or ["— none —"]
    selected_curr = cols[0].selectbox("Available curricula", curr_titles)

    # If somehow still empty, offer a one-click seed
    if not curricula:
        st.warning("No curricula found. Click below to add example curricula.")
        if st.button("➕ Seed example curricula (LOTO, Forklift, CNC, 5S, Fire Safety)"):
            save_json(os.path.join(KB_DIR, "curricula.json"), {"curricula": default_curricula()})
            st.experimental_rerun()

    dynamic_mode = cols[1].toggle("🤖 Dynamic Mode (ImpactXAI analyzes and adapts to your learning patterns)", value=True)
    voice_rate = cols[2].slider("🎙️ Voice WPM", 120, 220, 180, 10)

    # Voice choose
    v_eng = pyttsx3.init()
    voices = v_eng.getProperty("voices") or []
    v_map = {v.name: v.id for v in voices} or {"Default": None}
    v_sel = st.selectbox("Voice (auto/override)", list(v_map.keys()), index=0)
    voice_id = v_map[v_sel]

    # Current curriculum
    chosen = None
    if curricula and selected_curr != "— none —":
        idx = curr_titles.index(selected_curr)
        chosen = curricula[idx]
        p = load_prefs()
        p["last_curriculum"] = chosen["id"]
        save_prefs(p)

    st.markdown("## ▶️ Create Instructional Video")
    c1, c2 = st.columns([2,1])

    with c1:
        if st.button("⚡ Generate Now", type="primary", use_container_width=True):
            st.info("Building script & storyboard…")
            p = load_prefs()
            kb_context = json.dumps({
                "selected_curriculum": chosen,
                "kb": {k: kb[k] for k in ["machines","hazards","standards","sops"]},
                "preferences": {"language": p.get("language","en"), "pattern_hint": p.get("pattern_hint",""), "dynamic_mode": dynamic_mode}
            }, indent=2)[:9000]

            if dynamic_mode:
                directive = (
                    "Design a training module that matches my preferences: "
                    f"language='{p.get('language','en')}', pattern_hint='{p.get('pattern_hint','')}'. "
                    "Use the selected curriculum as a guide, but adjust as needed."
                )
            else:
                directive = f"Follow the selected curriculum strictly. language='{p.get('language','en')}'."

            prompt = (
                f"{directive}\n\n"
                "Return strictly JSON with keys:\n"
                " - narration: string (the full voiceover in the target language)\n"
                " - storyboard: list of frames, each: {\"Visual\": str, \"On-screen\": str}\n"
                "Aim for 3–8 frames. Keep on-screen text short and clear.\n\n"
                f"Context:\n{kb_context}"
            )

            raw = call_llm(prompt)
            parsed = extract_json_from_text(raw) or {
                "narration": heuristic_audio(),
                "storyboard": heuristic_storyboard().to_dict(orient="records")
            }

            narration = parsed.get("narration", heuristic_audio())
            storyboard_rows = parsed.get("storyboard", heuristic_storyboard().to_dict(orient="records"))

            st.info("Rendering video (audio if TTS available)…")
            out_path = os.path.join(OUT_DIR, "impactx_training_video.mp4")
            final_path = render_video_bulletproof(storyboard_rows, out_path, narration_text=narration,
                                                  persona_lang=p.get("language","en"), rate_wpm=voice_rate, voice_id=voice_id)
            st.success("Video generated successfully.")
            st.video(final_path)
            with open(final_path, "rb") as f:
                st.download_button("⬇ Download MP4", f, file_name=os.path.basename(final_path), use_container_width=True)

    with c2:
        st.markdown("#### 📘 Curriculum Snapshot")
        if chosen:
            st.markdown(f"**{chosen['title']}** — {chosen['duration_minutes']} min")
            st.caption(", ".join(chosen.get("target_roles", [])))
            st.markdown("**Objectives**")
            st.write("- " + "\n- ".join(chosen.get("objectives", [])))
            st.markdown("**Modules**")
            for m in chosen.get("modules", []):
                st.write(f"- **{m['title']}** — " + ", ".join(m.get("topics", [])))
            if chosen.get("standards_refs"):
                st.caption("References: " + ", ".join(chosen["standards_refs"]))
        else:
            st.info("No curricula file found. Using defaults.")

    st.markdown("## 🧪 Quick Test (LLM Free)")
    if st.button("Render Heuristic Test (3 slides)", use_container_width=True):
        p = load_prefs()
        sb = heuristic_storyboard().to_dict(orient="records")
        out = os.path.join(OUT_DIR, "impactx_test_video.mp4")
        final = render_video_bulletproof(sb, out, narration_text=heuristic_audio(),
                                         persona_lang=p.get("language","en"), rate_wpm=voice_rate, voice_id=voice_id)
        st.success("Test video ready.")
        st.video(final)
        with open(final, "rb") as f:
            st.download_button("⬇ Download Test MP4", f, file_name=os.path.basename(final), use_container_width=True)

    # ------------------ LLM Q&A (IN MAIN PAGE) ------------------
    st.markdown("---")
    st.markdown("## 💬 Ask ImpactX Knowledge Base")
    p = load_prefs()
    q = st.text_area("Ask a question about a machine, SOP, hazard, standard, or a curriculum:",
                     "Give me a 60-second refresher on LOTO in Dutch.")
    if st.button("Ask", use_container_width=True):
        ctx = json.dumps(kb, indent=2)[:9000]
        ans = call_llm(f"Use this manufacturing KB:\n{ctx}\n\nUser question (language={p.get('language','en')}):\n{q}")
        st.markdown(ans)

# ------------------ 📚 Knowledge Base tab ------------------
with tab_kb:
    st.subheader("ImpactX Knowledge Base Explorer")
    counts = kb_summary(kb)
    s1, s2, s3 = st.columns(3)
    s1.metric("Machines", counts["machines"])
    s2.metric("Hazards", counts["hazards"])
    s3.metric("Standards", counts["standards"])
    s4, s5 = st.columns(2)
    s4.metric("SOPs", counts["sops"])
    s5.metric("Curricula", counts["curricula"])

    section = st.selectbox("Section", ["Machines", "Hazards", "Standards", "SOPs", "Curricula"])
    df = kb_as_dataframe(kb, section)
    if df.empty:
        st.info("No data in this section yet.")
    else:
        st.dataframe(df, use_container_width=True)
        with st.expander("Quick chart", expanded=False):
            cat_cols = [c for c in df.columns if df[c].dtype == "object"]
            if cat_cols:
                vc_col = st.selectbox("Categorical column", cat_cols, index=0, key="kbtab_vc_col")
                vc = df[vc_col].astype(str).value_counts().head(12)
                st.bar_chart(vc)
            else:
                st.caption("No categorical columns to chart.")
        st.download_button(
            "⬇ Download this section as JSON",
            data=df.to_json(orient="records"),
            file_name=f"kb_{section.lower()}.json",
            mime="application/json",
            use_container_width=True
        )
