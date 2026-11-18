# Generative AI Code Platform

## Deploy free with Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py` and `requirements.txt`.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Select your repository, branch `main`, and main file `app.py`.
4. Click Deploy.

## Optional live Gemini AI
The app works without an API key using built-in demo examples.
For live generation/debugging/optimization, add this under Streamlit app Settings -> Secrets:
```toml
GEMINI_API_KEY = "your-api-key"
```
Never commit your API key to GitHub.

## Safety
This academic prototype executes code without hardened isolation. Do not run untrusted code. A production system needs isolated containers/VMs and strict resource, network and filesystem controls.
