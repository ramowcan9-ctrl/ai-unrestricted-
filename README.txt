CART3R AI - WINDOWS DESKTOP ASSISTANT
=====================================

WHAT IS INCLUDED
- Minimal Windows desktop chat interface
- Hybrid routing: try local Ollama first, then cloud API
- Local-only and cloud-only modes
- Conversation history saved automatically
- New chat and delete chat controls
- Settings for Ollama URL/model and OpenAI-compatible cloud URL/model
- Close and reopen like a normal Windows app
- No voice assistant

BUILD THE WINDOWS EXE
1. Install Python 3.11 or newer from https://www.python.org/downloads/
   During setup, enable "Add Python to PATH".
2. Extract this folder on Windows.
3. Double-click build_windows.bat.
4. The executable is created at dist\CART3R_AI.exe.
5. Copy the EXE to your Desktop or create a shortcut.

AI PROVIDERS
Local:
- Install Ollama from https://ollama.com/
- Start Ollama and download a model, e.g. `ollama pull llama3.2`
- Default URL: http://localhost:11434

Cloud:
- Open Settings in CART3R AI.
- Set your provider's OpenAI-compatible API base URL and model name.
- Add your API key.
- API usage may cost money depending on provider.

Hybrid:
- "Auto (local first)" tries Ollama first. If unavailable, it tries cloud.
- "Local only" never uses cloud.
- "Cloud only" uses the configured cloud provider.

DATA AND PRIVACY
- Chats and settings are stored in:
  %APPDATA%\CART3R\CART3R_AI
- The cloud API key is saved in settings.json in your Windows user profile.
  Anyone with access to that Windows account/files may be able to read it.
  For stronger protection, use a dedicated Windows account and device encryption.
- Do not paste passwords or other highly sensitive secrets into chat.

LIMITATIONS
- This app is a client interface, not a new foundation model.
- It does not bypass provider usage limits, safety policies, or subscription requirements.
- Cloud models require an API account/key. Local models depend on your PC hardware.
- It does not have unrestricted access to your computer or the internet.

AUTOMATIC WINDOWS BUILD (NO PYTHON INSTALL NEEDED ON YOUR PC)
1. Create a GitHub account if you do not already have one.
2. Create a new repository and upload the CONTENTS of this project folder.
   Make sure the .github/workflows/build-windows.yml file is included.
3. Open the repository's Actions tab.
4. Select "Build CART3R AI for Windows" and click "Run workflow" (or wait for
   the first push build to finish).
5. Open the completed workflow run, scroll to Artifacts, and download
   CART3R_AI-Windows. Extract it to get CART3R_AI.exe.

GitHub builds the EXE on a Windows runner. The EXE is not included in this
source ZIP; it is produced by the workflow and is downloadable as an artifact.
