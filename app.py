"""
Umoyo AI — Intelligent PCOS Health Companion
streamlit run app.py
"""

import os, json, warnings, datetime
import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ── SESSION STATE INITIALIZATION (ABSOLUTE TOP) ──────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hello.\n\n"
            "I'm Umoyo — your intelligent PCOS health companion.\n\n"
            "I can help you understand PCOS symptoms, nutrition, fitness, "
            "cycle patterns, mental wellness, and more.\n\n"
            "How can I support you today?"
        ),
    }]
if "symptom_log" not in st.session_state:
    st.session_state.symptom_log = {}
if "cycle_data" not in st.session_state:
    st.session_state.cycle_data = {"last_period": datetime.date.today(), "cycle_length": 28, "period_length": 5}
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []
if "wellness_score" not in st.session_state:
    st.session_state.wellness_score = 72
if "risk_result" not in st.session_state:
    st.session_state.risk_result = None

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
warnings.filterwarnings("ignore")
if os.path.exists(".env"):
    load_dotenv()

# Streamlit Cloud uses st.secrets; local uses .env / environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    st.error(
        "🔑 OpenAI API Key not found. "
        "Please set **OPENAI_API_KEY** in your Streamlit Secrets "
        "(Settings → Secrets) or in a local `.env` file."
    )
    # st.stop() # Removed st.stop() to allow testing UI without API key

client = OpenAI(api_key=api_key) if api_key else None

st.set_page_config(
    page_title="Umoyo AI · PCOS Health Companion",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Lato:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Lato',sans-serif;}
.stApp{background:#FBF7F9;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#FDE8EE 0%,#EEE6F8 100%);border-right:1px solid #EDD5E3;}
h1,h2,h3{font-family:'Cormorant Garamond',serif!important;color:#9B3D5C!important;}
.stButton>button{background:linear-gradient(135deg,#E8849A,#C96080)!important;color:#fff!important;border:none!important;border-radius:22px!important;font-family:'Lato',sans-serif!important;font-weight:600!important;letter-spacing:.04em!important;padding:.45rem 1.4rem!important;}
.stButton>button:hover{opacity:.88!important;}
.stChatMessage{background:#fff!important;border:1px solid #F5EAF1!important;border-radius:14px!important;margin-bottom:8px!important;}
.metric-card{background:#fff;border:1px solid #F5EAF1;border-radius:16px;padding:1.2rem;margin-bottom:12px;}
.metric-label{font-size:.72rem;color:#9E7A8E;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px;}
.metric-value{font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:700;color:#9B3D5C;line-height:1;}
.metric-sub{font-size:.72rem;color:#9E7A8E;margin-top:2px;}
.welcome-banner{background:linear-gradient(135deg,#FDE8EE 0%,#EEE6F8 100%);border:1px solid #EDD5E3;border-radius:20px;padding:2rem;margin-bottom:1.5rem;}
.welcome-tag{font-size:.72rem;color:#9E7A8E;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px;}
.welcome-title{font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:700;color:#9B3D5C;line-height:1.25;margin-bottom:6px;}
.welcome-sub{font-size:.85rem;color:#6B4A5E;font-weight:300;}
.disclaimer{background:#EEE6F8;border-radius:10px;padding:.75rem 1rem;font-size:.75rem;color:#6B4A5E;text-align:center;margin-top:2rem;}
.tag-rose{display:inline-block;background:#FDE8EE;color:#C96080;font-size:.65rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:3px 10px;border-radius:10px;}
.insight-card{background:#fff;border:1px solid #F5EAF1;border-radius:12px;padding:.9rem;margin-bottom:10px;}
.risk-low{background:#EAFAF0;border-left:4px solid #6BAF8A;border-radius:10px;padding:1rem;}
.risk-mod{background:#FFF8EC;border-left:4px solid #C5A070;border-radius:10px;padding:1rem;}
.risk-high{background:#FDE8EE;border-left:4px solid #C96080;border-radius:10px;padding:1rem;}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are Umoyo, a warm, professional, and knowledgeable AI health companion "
    "specialising in PCOS (Polycystic Ovary Syndrome). Provide accurate, evidence-based "
    "information about symptoms, management, nutrition, fitness, and mental wellness. "
    "Be empathetic, supportive, and encouraging. "
    "CRITICAL: You are NOT a doctor. Never diagnose. Always encourage users to consult "
    "qualified healthcare professionals. Keep responses conversational and clear. "
    "If someone asks 'Who created you?' or similar identity questions, respond ONLY with: "
    "'I was created by Novricana Lungu of HealingTechnologies.'"
)

DISCLAIMER = (
    "⚕ Umoyo is an AI health companion for education and wellness support only. "
    "It is not a substitute for professional medical advice, diagnosis, or treatment. "
    "Always consult a qualified healthcare provider for medical concerns."
)

SUGGESTED_QUESTIONS = [
    "What are the most common PCOS symptoms?",
    "How does diet affect PCOS hormones?",
    "What exercises help with PCOS?",
    "Can PCOS affect fertility?",
    "How do I manage irregular periods naturally?",
    "What is insulin resistance and how does it relate to PCOS?",
]

# ── Load ML model ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model():
    try:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_artifacts")
        model   = joblib.load(os.path.join(base, "best_svc_model.joblib"))
        scaler  = joblib.load(os.path.join(base, "scaler.joblib"))
        with open(os.path.join(base, "feature_names.json")) as f:
            features = json.load(f)
        return model, scaler, features
    except Exception as e:
        st.error(f"Error loading model artifacts: {e}")
        return None, None, None

model, scaler, feature_names = load_model()

# ── Logging helper ──────────────────────────────────────────────────────────
def save_logs_to_file():
    """Save all session logs to a JSON file."""
    try:
        # Use a directory that is likely writable in any environment
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"umoyo_logs_{timestamp}.json")
        
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "symptom_log": st.session_state.symptom_log,
            "cycle_data": {k: str(v) for k, v in st.session_state.cycle_data.items()},
            "mood_log": st.session_state.mood_log,
            "wellness_score": st.session_state.wellness_score,
            "risk_result": st.session_state.risk_result,
            "messages_count": len(st.session_state.messages)
        }
        
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)
        
        return True, log_file
    except Exception as e:
        return False, str(e)

# ── OpenAI helper ──────────────────────────────────────────────────────────
def stream_umoyo(messages: list, placeholder):
    """Call OpenAI and stream the response word-by-word into `placeholder`."""
    if not client:
        msg = "⚠️ OpenAI API Key is missing. Please set it in secrets or .env."
        placeholder.markdown(msg)
        return msg
        
    try:
        import time
        # Prepare messages
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in messages:
            api_messages.append({"role": m["role"], "content": m["content"]})
            
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=api_messages,
            stream=False,
        )
        full = response.choices[0].message.content

        # Simulated streaming effect
        curr = ""
        for word in full.split(" "):
            curr += word + " "
            placeholder.markdown(curr + "▌")
            time.sleep(0.03)

        placeholder.markdown(full)
        return full
    except Exception as e:
        msg = f"⚠️ Could not reach the AI: {e}. Please try again."
        placeholder.markdown(msg)
        return msg

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 .5rem;'>
        <div style='width:56px;height:56px;border-radius:50%;
            background:linear-gradient(135deg,#E8849A,#C96080);
            display:inline-flex;align-items:center;justify-content:center;
            font-size:26px;margin-bottom:8px;'>🌸</div>
        <div style='font-family:Cormorant Garamond,serif;font-size:1.5rem;
            font-weight:700;color:#9B3D5C;'>UMOYO AI</div>
        <div style='font-size:.68rem;color:#9E7A8E;letter-spacing:.1em;
            text-transform:uppercase;'>PCOS Health Companion</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigate", [
        "💬 AI Companion", "🏠 Home", "📊 Risk Assessment",
        "📅 Symptom Tracker", "🌙 Cycle Tracker", "✨ Wellness Hub"
    ], label_visibility="collapsed")
    st.markdown("---")
    
    # Export logs button
    if st.button("📥 Export Logs", use_container_width=True):
        success, result = save_logs_to_file()
        if success:
            st.success(f"✅ Logs saved locally: {result}")
            # Provide download link for the JSON
            with open(result, "r") as f:
                st.download_button(
                    label="Download JSON Log",
                    data=f.read(),
                    file_name=os.path.basename(result),
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.error(f"❌ Failed to save logs: {result}")
    
    st.markdown(f"<div class='disclaimer' style='margin-top:0;font-size:.68rem;'>{DISCLAIMER}</div>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# AI COMPANION
# ══════════════════════════════════════════════════════════════════════════
if page == "💬 AI Companion":
    st.markdown("## AI Companion")
    st.markdown("<p style='color:#9E7A8E;font-size:.85rem;margin-top:-12px;margin-bottom:16px;'>"
                "Ask me anything about PCOS, nutrition, fitness, or mental wellness.</p>",
                unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if len(st.session_state.messages) == 1:
        st.markdown("**Try asking:**")
        cols = st.columns(3)
        for i, q in enumerate(SUGGESTED_QUESTIONS):
            with cols[i % 3]:
                if st.button(q, key=f"sug_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.rerun()

    if prompt := st.chat_input("Ask Umoyo anything about PCOS…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Handle response generation after rerun to ensure prompt is displayed first
    if st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            ph = st.empty()
            reply = stream_umoyo(st.session_state.messages, ph)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("Clear conversation", type="secondary"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════
elif page == "🏠 Home":
    st.markdown("""
    <div class='welcome-banner'>
        <div class='welcome-tag'>Takulandilani</div>
        <div class='welcome-title'>Welcome — Umoyo is here<br>to support your journey.</div>
        <div class='welcome-sub'>Your intelligent PCOS health companion, ready to help.</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    logged_today = len(st.session_state.symptom_log.get(today_str, {}))
    
    # Calculate cycle day
    last_p = st.session_state.cycle_data["last_period"]
    if last_p:
        delta = (datetime.date.today() - last_p).days
        cycle_day = (delta % st.session_state.cycle_data["cycle_length"]) + 1
        cycle_text = f"Day {cycle_day}"
    else:
        cycle_text = "N/A"

    for col, label, val, sub in [
        (c1, "Wellness Score", st.session_state.wellness_score, "out of 100"),
        (c2, "Cycle Day", cycle_text, "Estimated"),
        (c3, "Symptoms Today", logged_today, "logged today"),
        (c4, "Mood Entries", len(st.session_state.mood_log), "total tracked"),
    ]:
        col.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{val}</div>
            <div class='metric-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    left, right = st.columns([1, 1.1])

    with left:
        st.markdown("### Quick Actions")
        st.info("Use the sidebar to navigate to any section.")
        st.markdown("### Daily Insights")
        for tag, text in [
            ("Education", "Irregular cycles are one of the most common PCOS indicators. Tracking helps identify patterns."),
            ("Nutrition", "Anti-inflammatory foods like berries, leafy greens, and fatty fish support PCOS management."),
            ("Fitness", "Low-impact exercises like yoga and walking help regulate hormones naturally."),
        ]:
            st.markdown(f"""
            <div class='insight-card'>
                <span class='tag-rose'>{tag}</span>
                <p style='margin:6px 0 0;font-size:.82rem;color:#6B4A5E;line-height:1.5;'>{text}</p>
            </div>""", unsafe_allow_html=True)

    with right:
        st.markdown("### Ask Umoyo Now")
        last_msg = next(
            (m for m in reversed(st.session_state.messages) if m["role"] == "assistant"), None)
        if last_msg:
            preview = last_msg["content"][:300] + ("…" if len(last_msg["content"]) > 300 else "")
            st.markdown(f"""
            <div style='background:#fff;border:1px solid #EDD5E3;border-radius:14px;padding:1rem;margin-bottom:12px;'>
                <div style='display:flex;align-items:center;gap:10px;padding-bottom:8px;border-bottom:1px solid #F5EAF1;margin-bottom:8px;'>
                    <div style='width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#E8849A,#C96080);display:flex;align-items:center;justify-content:center;font-size:14px;'>🌸</div>
                    <div>
                        <div style='font-family:Cormorant Garamond,serif;font-weight:700;font-size:.95rem;color:#9B3D5C;'>Umoyo</div>
                        <div style='font-size:.65rem;color:#6BAF8A;font-weight:600;'>● Online</div>
                    </div>
                </div>
                <div style='font-size:.85rem;color:#2D1A26;line-height:1.6;white-space:pre-wrap;'>{preview}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("**Suggested questions — click to ask:**")
        for q in SUGGESTED_QUESTIONS[:4]:
            if st.button(q, key=f"home_{q}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

    st.markdown(f"<div class='disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# RISK ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════
elif page == "📊 Risk Assessment":
    st.markdown("## Risk Assessment")
    st.markdown("<p style='color:#9E7A8E;font-size:.85rem;margin-top:-12px;margin-bottom:24px;'>"
                "Our AI model estimates your PCOS risk based on clinical markers.</p>",
                unsafe_allow_html=True)

    with st.form("risk_form"):
        c1, c2 = st.columns(2)
        age    = c1.number_input("Age", 15, 50, 25)
        weight = c2.number_input("Weight (kg)", 30.0, 200.0, 65.0)
        height = c1.number_input("Height (cm)", 100.0, 250.0, 165.0)
        cycle  = c2.selectbox("Cycle Regularity", ["Regular", "Irregular"])

        submitted = st.form_submit_button("Analyze Risk Profile")

        if submitted:
            if model and scaler:
                try:
                    bmi = round(weight / ((height / 100) ** 2), 2)
                    irregularity = 0 if cycle == "Regular" else 1
                    input_df = pd.DataFrame([[age, bmi]], columns=["age", "bmi"])
                    scaled = scaler.transform(input_df)
                    scaled_df = pd.DataFrame(scaled, columns=["age", "bmi"])
                    scaled_df["menstrual_irregularity"] = irregularity
                    scaled_df = scaled_df[["age", "bmi", "menstrual_irregularity"]]
                    pred = model.predict(scaled_df)[0]
                    prob = model.predict_proba(scaled_df)[0][1]
                    st.session_state.risk_result = {"pred": pred, "prob": prob}
                    st.success("✅ Risk assessment completed successfully!")
                except Exception as e:
                    st.error(f"❌ Error during risk assessment: {str(e)}")
            else:
                st.error("Model artifacts not loaded.")

    if st.session_state.risk_result:
        res      = st.session_state.risk_result
        prob_pct = res["prob"] * 100
        if prob_pct < 30:
            st.markdown("<div class='risk-low'><strong>Low Risk Profile</strong><br>Your clinical markers suggest a low probability of PCOS.</div>", unsafe_allow_html=True)
        elif prob_pct < 70:
            st.markdown("<div class='risk-mod'><strong>Moderate Risk Profile</strong><br>Some markers align with PCOS patterns. Further clinical review is recommended.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='risk-high'><strong>High Risk Profile</strong><br>Your profile strongly aligns with PCOS clinical markers. Please consult a specialist.</div>", unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode  = "gauge+number",
            value = prob_pct,
            title = {"text": "PCOS Risk Probability (%)", "font": {"family": "Cormorant Garamond", "size": 20}},
            gauge = {
                "axis":  {"range": [0, 100]},
                "bar":   {"color": "#9B3D5C"},
                "steps": [
                    {"range": [0,  30],  "color": "#EAFAF0"},
                    {"range": [30, 70],  "color": "#FFF8EC"},
                    {"range": [70, 100], "color": "#FDE8EE"},
                ],
            }
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# SYMPTOM TRACKER
# ══════════════════════════════════════════════════════════════════════════
elif page == "📅 Symptom Tracker":
    st.markdown("## Symptom Tracker")
    date     = st.date_input("Select Date", datetime.date.today())
    date_str = date.strftime("%Y-%m-%d")

    symptoms = ["Acne", "Hair Loss", "Excess Hair", "Fatigue", "Mood Swings", "Bloating"]
    current  = st.session_state.symptom_log.get(date_str, {})

    st.markdown("### Log Symptoms")
    new_log = {}
    cols = st.columns(3)
    for i, s in enumerate(symptoms):
        new_log[s] = cols[i % 3].checkbox(s, value=current.get(s, False))

    if st.button("Save Log"):
        st.session_state.symptom_log[date_str] = new_log
        st.success(f"✅ Log updated and saved for {date_str}!")
        # Automatically trigger a background save
        save_logs_to_file()

# ══════════════════════════════════════════════════════════════════════════
# CYCLE TRACKER
# ══════════════════════════════════════════════════════════════════════════
elif page == "🌙 Cycle Tracker":
    st.markdown("## Cycle Tracker & Prediction")
    
    with st.expander("Update Cycle Settings", expanded=True):
        st.session_state.cycle_data["last_period"]   = st.date_input("Last Period Start Date", value=st.session_state.cycle_data.get("last_period", datetime.date.today()))
        st.session_state.cycle_data["cycle_length"]  = st.slider("Average Cycle Length", 21, 45, st.session_state.cycle_data.get("cycle_length", 28))
        st.session_state.cycle_data["period_length"] = st.slider("Average Period Length", 2, 10, st.session_state.cycle_data.get("period_length", 5))

    # Prediction Logic
    last_p = st.session_state.cycle_data["last_period"]
    cycle_len = st.session_state.cycle_data["cycle_length"]
    next_p = last_p + datetime.timedelta(days=cycle_len)
    ovulation = last_p + datetime.timedelta(days=cycle_len - 14)
    
    st.markdown("### Predictions")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Next Period</div>
        <div class='metric-value' style='font-size:1.5rem;'>{next_p.strftime('%b %d, %Y')}</div>
        <div class='metric-sub'>Estimated Start</div>
    </div>""", unsafe_allow_html=True)
    
    c2.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Ovulation Day</div>
        <div class='metric-value' style='font-size:1.5rem;'>{ovulation.strftime('%b %d, %Y')}</div>
        <div class='metric-sub'>Fertile Window Peak</div>
    </div>""", unsafe_allow_html=True)
    
    days_to_go = (next_p - datetime.date.today()).days
    c3.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Countdown</div>
        <div class='metric-value' style='font-size:1.5rem;'>{days_to_go} Days</div>
        <div class='metric-sub'>Until next cycle</div>
    </div>""", unsafe_allow_html=True)

    st.info("💡 PCOS can cause irregular cycles. These predictions are estimates based on your provided average cycle length.")

# ══════════════════════════════════════════════════════════════════════════
# WELLNESS HUB
# ══════════════════════════════════════════════════════════════════════════
elif page == "✨ Wellness Hub":
    st.markdown("## Wellness Hub")
    tab1, tab2 = st.tabs(["Nutrition", "Fitness"])

    with tab1:
        st.markdown("### PCOS Nutrition")
        st.markdown("Focus on low-glycemic, anti-inflammatory foods.")
        if st.button("Generate My 5-Day Meal Plan"):
            with st.chat_message("assistant"):
                ph = st.empty()
                stream_umoyo([{"role": "user", "content": "Generate a 5-day PCOS-friendly low-GI meal plan."}], ph)

    with tab2:
        st.markdown("### PCOS Fitness")
        st.markdown("Strength training and low-impact cardio are key.")
        if st.button("Generate My Weekly Fitness Plan"):
            with st.chat_message("assistant"):
                ph = st.empty()
                stream_umoyo([{"role": "user", "content": "Generate a weekly PCOS fitness plan including strength and cardio."}], ph)

# ── Footer disclaimer (always shown) ──────────────────────────────────────
st.markdown(f"<div class='disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)
