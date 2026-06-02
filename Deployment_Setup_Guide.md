# 🚀 Deployment Setup Guide: OPENAI_API_KEY

To make your chatbot work, you need to provide a valid OpenAI API key to the application. Since your code is built with Streamlit, here is how to set it up in different environments.

---

## 1. Streamlit Community Cloud (Recommended)
If you are hosting your app on [share.streamlit.io](https://share.streamlit.io), follow these steps:

1.  **Log in** to your Streamlit Cloud dashboard.
2.  Find your app and click the **three dots (⋮)** next to it.
3.  Select **Settings**.
4.  Navigate to the **Secrets** tab on the left sidebar.
5.  In the text area, paste the following (replacing the placeholder with your actual key):
    ```toml
    OPENAI_API_KEY = "sk-proj-..."
    ```
6.  Click **Save**. The app will automatically reboot and the chatbot should start responding.

---

## 2. Render Deployment
If you are using [Render.com](https://render.com), follow these steps:

1.  Go to your **Dashboard** and select your Web Service.
2.  Click on the **Environment** tab.
3.  Click **Add Environment Variable**.
4.  Set the **Key** to: `OPENAI_API_KEY`
5.  Set the **Value** to your actual OpenAI key: `sk-proj-...`
6.  Click **Save Changes**. Render will trigger a new deployment with the updated key.

---

## 3. Local Development (Testing on your PC)
To test the app locally before deploying:

1.  Create a file named `.env` in the root folder of your project (where `app.py` is).
2.  Add the following line to the file:
    ```bash
    OPENAI_API_KEY=sk-proj-your-real-key-here
    ```
3.  Restart your Streamlit app: `streamlit run app.py`

---

## ⚠️ Critical Reminders
*   **Key Name:** Ensure the name is exactly `OPENAI_API_KEY`. Your code specifically checks for this name on lines 43-46 of `app.py`.
*   **Account Credits:** Ensure your OpenAI account has a positive balance. Even "Free Trial" accounts sometimes require you to have at least $5 in credits to use the API consistently.
*   **Model Access:** Your code uses `gpt-4o-mini`. Most new OpenAI accounts have access to this by default, but double-check your [OpenAI Dashboard](https://platform.openai.com/usage) to ensure you aren't hitting a rate limit.
