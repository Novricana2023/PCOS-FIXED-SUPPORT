# 🌸 Umoyo AI — Intelligent PCOS Health Companion

> *"Umoyo" means Life in Chewa.*

Umoyo AI is a premium, AI-powered PCOS health companion built with Streamlit and OpenAI. It provides education, wellness tracking, cycle prediction, symptom logging, and personalised AI guidance — all in a beautiful, accessible interface.

---

## Features

| Feature | Description |
|---|---|
| 💬 AI Companion | Streaming chat with OpenAI — word-by-word responses |
| 📊 Risk Assessment | ML model + AI analysis of PCOS risk factors |
| 📅 Symptom Tracker | Daily symptom logging with trend charts |
| 🌙 Cycle Tracker | Period prediction + ovulation estimates |
| ✨ Wellness Hub | Mood journal, fitness plans, nutrition guide |

---

## Quick Start (Local)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/umoyo-ai.git
cd umoyo-ai
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```
Get your real key from [platform.openai.com](https://platform.openai.com).

### 5. Run the app
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## Project Structure

```
Umoyo_AI_Streamlit/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── .env                            # API key (create this file)
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── model_artifacts/
│   ├── best_svc_model.joblib       # Trained PCOS SVC model
│   ├── scaler.joblib               # Feature scaler
│   └── feature_names.json          # Model feature names
└── .streamlit/
    ├── config.toml                 # Streamlit theme + server config
    └── secrets.toml.example        # Secrets template for Streamlit Cloud
```

---

## Deployment Guide

### GitHub

```bash
# Initialise git (if not already done)
git init
git add .
git commit -m "Initial commit — Umoyo AI"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/umoyo-ai.git
git branch -M main
git push -u origin main
```

> ⚠️ Make sure `.env` is in your `.gitignore`. Never push your API key.

---

### Streamlit Community Cloud (Free — Recommended)

1. Push your code to GitHub (see above)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repository, branch `main`, and set **Main file path** to `app.py`
5. Click **Advanced settings → Secrets** and paste:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```
6. Click **Deploy**

---

### Render (Free tier available)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Set:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `streamlit run app.py --server.port $PORT --server.headless true`
5. Under **Environment Variables**, add:
   - Key: `OPENAI_API_KEY`
   - Value: your OpenAI API key
6. Click **Create Web Service**

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key from [platform.openai.com](https://platform.openai.com) |

---

## Tech Stack

- **Frontend / App:** [Streamlit](https://streamlit.io)
- **AI:** [OpenAI GPT-4o-mini](https://openai.com)
- **ML Model:** Scikit-learn SVC (trained PCOS risk classifier)
- **Charts:** Plotly
- **Data:** Pandas + NumPy

---

## Medical Disclaimer

Umoyo AI is an educational health companion only. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for any medical concerns.

---

## License

MIT © Umoyo AI
