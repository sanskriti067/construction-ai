import json
import urllib.parse

import streamlit as st
from PIL import Image

try:
    from google import genai
    from google.genai import types
except ImportError:  # app still runs in demo mode
    genai = None

MODEL = "gemini-3.8-flash"  # change to any current Gemini model listed in AI Studio

st.set_page_config(page_title="Construction Intelligence Platform", page_icon="🏗️", layout="wide")
st.markdown(
    "<style>.stMetric{background:rgba(128,128,128,0.15);padding:12px;border-radius:10px}"
    "h1{color:#12355b}</style>",
    unsafe_allow_html=True,
)

# ---------------- Sidebar ----------------
st.sidebar.title("🏗️ Control Panel")
api_key = st.sidebar.text_input("Google Gemini API key", type="password")
live = bool(api_key) and genai is not None
st.sidebar.success("Live AI mode" if live else "Demo mode (no key)")
st.sidebar.markdown(
    "**Architecture**\n\nStreamlit UI → Gemini multimodal model → strict JSON contract → rendered cards"
)

client = genai.Client(api_key=api_key) if live else None


def ask_json(prompt, image, demo):
    """Send prompt (+image) to Gemini, force JSON, fall back to demo data on any failure."""
    if not live:
        return demo
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=[prompt, image],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(resp.text)
    except Exception as e:
        st.warning(f"AI call failed ({e}). Showing demo output instead.")
        return demo


def show_image_upload(label, key):
    f = st.file_uploader(label, type=["jpg", "jpeg", "png"], key=key)
    if f:
        try:
            img = Image.open(f).convert("RGB")
            st.image(img, use_container_width=True)
            return img
        except Exception:
            st.error("Could not read that image. Please upload a valid JPG/PNG.")
    return None


SEV_ICON = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}

st.title("Multimodal Construction Intelligence Platform")
t1, t2, t3, t4 = st.tabs(
    ["🦺 Site Safety & PPE", "🧱 Crack Diagnostics", "📐 Planning & Valuation", "🌦️ Daily Assistant"]
)

# ---------------- Tab 1: Safety ----------------
with t1:
    st.subheader("Site Safety & PPE Audit")
    img = show_image_upload("Upload a construction site photo", "safety")
    if img and st.button("Run safety audit", type="primary"):
        prompt = (
            "You are a construction safety auditor (OSHA / IS 456 context). Analyze this site photo. "
            "Return ONLY JSON: {\"safety_score\": int 0-100, \"overall_status\": str, "
            "\"ppe_detection\": {\"helmet\": bool, \"hi_vis_vest\": bool, \"safety_boots\": bool, \"harness\": bool}, "
            "\"hazards\": [{\"hazard\": str, \"severity\": \"Low|Medium|High|Critical\", \"remedy\": str}]}"
        )
        demo = {
            "safety_score": 62,
            "overall_status": "Needs Improvement (demo data)",
            "ppe_detection": {"helmet": True, "hi_vis_vest": False, "safety_boots": True, "harness": False},
            "hazards": [
                {"hazard": "Worker at height without harness", "severity": "Critical", "remedy": "Stop work; provide full-body harness."},
                {"hazard": "Exposed rebar ends", "severity": "Medium", "remedy": "Fit rebar caps."},
            ],
        }
        with st.spinner("Analyzing..."):
            r = ask_json(prompt, img, demo)
        c1, c2 = st.columns(2)
        c1.metric("Safety score", f"{r.get('safety_score', '?')}/100")
        c2.metric("Status", r.get("overall_status", "?"))
        st.markdown("**PPE checklist**")
        for k, v in r.get("ppe_detection", {}).items():
            st.write(("✅" if v else "❌") + " " + k.replace("_", " ").title())
        st.markdown("**Hazards**")
        for h in r.get("hazards", []):
            st.write(f"{SEV_ICON.get(h.get('severity'), '⚪')} **{h.get('hazard')}** ({h.get('severity')}) — {h.get('remedy')}")
        st.download_button("Download JSON report", json.dumps(r, indent=2), "safety_report.json")

# ---------------- Tab 2: Cracks ----------------
with t2:
    st.subheader("Crack Diagnostics & Structural Integrity")
    img = show_image_upload("Upload a wall / concrete surface photo", "crack")
    if img and st.button("Diagnose crack", type="primary"):
        prompt = (
            "You are a structural engineer. Classify the defect in this image. Return ONLY JSON: "
            "{\"defect_type\": \"Hairline|Settlement|Structural Shear|Thermal Expansion|Spalling\", "
            "\"estimated_width_mm\": number, \"severity\": \"Low|Medium|High|Critical\", "
            "\"root_causes\": [str], \"repairs\": [str], \"urgency\": str}"
        )
        demo = {
            "defect_type": "Settlement",
            "estimated_width_mm": 3.5,
            "severity": "High",
            "root_causes": ["Differential foundation settlement", "Poor soil compaction"],
            "repairs": ["Epoxy injection", "Structural re-grouting"],
            "urgency": "Inspect within 7 days (demo data)",
        }
        with st.spinner("Analyzing..."):
            r = ask_json(prompt, img, demo)
        c1, c2, c3 = st.columns(3)
        c1.metric("Defect", r.get("defect_type", "?"))
        c2.metric("Width (mm)", r.get("estimated_width_mm", "?"))
        c3.metric("Severity", f"{SEV_ICON.get(r.get('severity'), '')} {r.get('severity', '?')}")
        st.write("**Root causes:**", ", ".join(r.get("root_causes", [])))
        st.write("**Recommended repairs:**", ", ".join(r.get("repairs", [])))
        st.info(f"Urgency: {r.get('urgency', '?')}")
        st.caption("AI-generated guidance. Have a licensed engineer inspect before acting.")

# ---------------- Tab 3: Planning & valuation ----------------
with t3:
    st.subheader("Project Planning & Real Estate Valuation (INR)")
    c1, c2 = st.columns(2)
    stype = c1.selectbox("Structure type", ["Residential", "Commercial", "Industrial"])
    sqft = c1.number_input("Built-up area (sq ft)", 200, 500000, 2000, step=100)
    tier = c2.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
    done = c2.slider("Completion %", 0, 100, 40)

    base = {"Residential": 1800, "Commercial": 2400, "Industrial": 2000}[stype]
    mult = {"Tier 1": 1.2, "Tier 2": 1.0, "Tier 3": 0.85}[tier]
    budget = sqft * base * mult
    spent = budget * done / 100
    value = budget * 1.6 * done / 100  # simple market-value heuristic


    def inr(x):
        return f"₹{x/1e7:.2f} Cr" if x >= 1e7 else f"₹{x/1e5:.2f} Lakh"


    m1, m2, m3 = st.columns(3)
    m1.metric("Total budget", inr(budget))
    m2.metric("Capex incurred", inr(spent))
    m3.metric("Current asset value", inr(value))
    m4, m5 = st.columns(2)
    m4.metric("Cement needed", f"{int(sqft * 0.4):,} bags")
    m5.metric("Steel needed", f"{int(sqft * 4):,} kg")
    st.progress(done / 100, text=f"Milestone progress: {done}%")
    st.caption("Estimates only, not a certified valuation.")

    if st.button("Generate conceptual 3D rendering"):
        p = f"architectural 3D render of a modern {stype.lower()} building, photorealistic, daylight"
        st.image("https://image.pollinations.ai/prompt/" + urllib.parse.quote(p), caption="Pollinations AI concept")

# ---------------- Tab 4: Weather + chatbot ----------------
with t4:
    st.subheader("Weather-Aware Advisory")
    w = st.selectbox("Today's conditions", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    advice = {
        "Normal": ("success", "Normal operations. Do routine PPE and equipment checks."),
        "High Wind": ("error", "Suspend crane and lifting operations. Secure scaffolding sheets and loose materials."),
        "Heavy Rain": ("warning", "Halt concrete pouring, cover curing areas, isolate temporary electrical connections."),
        "Extreme Heat": ("warning", "Schedule breaks and hydration, pour concrete early morning, wet-cure for extra days."),
    }[w]
    getattr(st, advice[0])(advice[1])

    st.subheader("Construction Assistant")
    if "chat" not in st.session_state:
        st.session_state.chat = []
    for m in st.session_state.chat:
        st.chat_message(m["role"]).write(m["text"])
    q = st.chat_input("Ask a construction question")
    if q:
        st.session_state.chat.append({"role": "user", "text": q})
        if live:
            try:
                history = "\n".join(f"{m['role']}: {m['text']}" for m in st.session_state.chat)
                resp = client.models.generate_content(
                    model=MODEL,
                    contents=history,
                    config=types.GenerateContentConfig(
                        system_instruction="You are a concise, practical construction engineering assistant. "
                        "Mention safety and IS code considerations where relevant."
                    ),
                )
                reply = resp.text
            except Exception as e:
                reply = f"AI call failed: {e}"
        else:
            reply = "(Demo mode) Add a Gemini API key in the sidebar for live answers."
        st.session_state.chat.append({"role": "assistant", "text": reply})
        st.rerun()
