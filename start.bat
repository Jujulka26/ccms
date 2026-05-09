@echo off
cd /d "C:\Users\My PC\OneDrive\Desktop\ccms"

echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "c:\python_env\py311_env\Scripts\activate && uvicorn backend.main:app --reload"

timeout /t 3 /nobreak

echo Starting Streamlit Frontend...
start "Streamlit Frontend" cmd /k "c:\python_env\py311_env\Scripts\activate && streamlit run app.py"

timeout /t 3 /nobreak

echo Starting Cloudflare Tunnel...
start "Cloudflare Tunnel" cmd /k "cloudflared tunnel run ccmatch"

echo All services started! Access your app at https://cc-match.com
