import json
import os
import threading
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

APP_NAME = "CART3R AI"
APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "CART3R" / "CART3R_AI"
CONFIG_FILE = APP_DIR / "settings.json"
HISTORY_FILE = APP_DIR / "conversations.json"

DEFAULTS = {
    "mode": "Auto (local first)",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3.2",
    "cloud_url": "https://api.openai.com/v1",
    "cloud_model": "gpt-4o-mini",
    "api_key": "",
    "system_prompt": "You are CART3R AI, a helpful, capable desktop assistant. Be accurate, practical, and clear."
}

class Cart3rApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CART3R AI")
        self.root.geometry("1080x720")
        self.root.minsize(800, 560)
        self.root.configure(bg="#f4f5f7")
        self.settings = self.load_json(CONFIG_FILE, DEFAULTS.copy())
        self.conversations = self.load_json(HISTORY_FILE, [])
        self.current_id = None
        self.busy = False
        self._style()
        self._build()
        if self.conversations:
            self.current_id = self.conversations[-1].get("id")
            self.render_conversation()
        else:
            self.new_chat()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_json(self, path, default):
        try:
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
        except Exception:
            pass
        return default

    def save_json(self, path, data):
        APP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(path)

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TButton", font=("Segoe UI", 10), padding=(11, 7))
        style.configure("Accent.TButton", background="#242a35", foreground="white")
        style.map("Accent.TButton", background=[("active", "#3b4352")])
        style.configure("TCombobox", padding=6)
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _build(self):
        top = tk.Frame(self.root, bg="#ffffff", height=64, highlightbackground="#e2e5e9", highlightthickness=1)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="CART3R AI", bg="#ffffff", fg="#202633",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=22)
        tk.Label(top, text="DESKTOP ASSISTANT", bg="#ffffff", fg="#7a8290",
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 10), pady=(8, 0))
        ttk.Button(top, text="Settings", command=self.open_settings).pack(side="right", padx=18, pady=13)
        ttk.Button(top, text="＋ New chat", command=self.new_chat).pack(side="right", padx=5, pady=13)

        body = tk.Frame(self.root, bg="#f4f5f7")
        body.pack(fill="both", expand=True)
        side = tk.Frame(body, bg="#ffffff", width=245, highlightbackground="#e2e5e9", highlightthickness=1)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="YOUR CHATS", bg="#ffffff", fg="#7a8290",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(18, 8))
        self.chat_list = tk.Listbox(side, bd=0, highlightthickness=0, activestyle="none",
                                    bg="#ffffff", fg="#303744", selectbackground="#e8ebf0",
                                    selectforeground="#202633", font=("Segoe UI", 10))
        self.chat_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.chat_list.bind("<<ListboxSelect>>", self.select_chat)
        ttk.Button(side, text="Delete selected chat", command=self.delete_chat).pack(fill="x", padx=12, pady=(0, 14))

        main = tk.Frame(body, bg="#f4f5f7")
        main.pack(side="left", fill="both", expand=True)
        self.heading = tk.Label(main, text="New conversation", bg="#f4f5f7", fg="#202633",
                                 font=("Segoe UI", 16, "bold"))
        self.heading.pack(anchor="w", padx=26, pady=(20, 3))
        self.provider_label = tk.Label(main, text=self.provider_status(), bg="#f4f5f7", fg="#7a8290",
                                       font=("Segoe UI", 9))
        self.provider_label.pack(anchor="w", padx=27, pady=(0, 10))

        chatwrap = tk.Frame(main, bg="#ffffff", highlightbackground="#e2e5e9", highlightthickness=1)
        chatwrap.pack(fill="both", expand=True, padx=22, pady=(0, 12))
        self.chat_text = tk.Text(chatwrap, wrap="word", bd=0, padx=18, pady=16,
                                 bg="#ffffff", fg="#252c38", font=("Segoe UI", 10),
                                 state="disabled", spacing1=3, spacing3=8)
        scroll = ttk.Scrollbar(chatwrap, command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=scroll.set)
        self.chat_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.chat_text.tag_configure("user", foreground="#1c4e80", font=("Segoe UI", 10, "bold"))
        self.chat_text.tag_configure("assistant", foreground="#202633", font=("Segoe UI", 10, "bold"))
        self.chat_text.tag_configure("body", foreground="#303744")

        compose = tk.Frame(main, bg="#f4f5f7")
        compose.pack(fill="x", padx=22, pady=(0, 18))
        self.entry = tk.Text(compose, height=3, wrap="word", bd=1, relief="solid",
                             highlightthickness=1, highlightbackground="#d9dde3",
                             font=("Segoe UI", 10), padx=10, pady=8)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Control-Return>", lambda e: self.send_message())
        self.send_btn = ttk.Button(compose, text="Send  ➤", style="Accent.TButton", command=self.send_message)
        self.send_btn.pack(side="left", padx=(10, 0), fill="y")
        bottom = tk.Label(main, text="Enter a message  •  Ctrl+Enter to send  •  Chats save automatically",
                          bg="#f4f5f7", fg="#8a919d", font=("Segoe UI", 8))
        bottom.pack(anchor="center", pady=(0, 8))
        self.refresh_chat_list()

    def provider_status(self):
        mode = self.settings.get("mode", "Auto (local first)")
        return f"Engine: {mode}  |  Local: {self.settings.get('ollama_model')}  |  Cloud: {self.settings.get('cloud_model')}"

    def current_chat(self):
        for c in self.conversations:
            if c.get("id") == self.current_id:
                return c
        return None

    def new_chat(self):
        c = {"id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
             "title": "New conversation", "messages": [], "updated": datetime.now().isoformat(timespec="seconds")}
        self.conversations.append(c)
        self.current_id = c["id"]
        self.persist()
        self.refresh_chat_list()
        self.render_conversation()
        self.entry.focus_set()

    def select_chat(self, _event=None):
        selection = self.chat_list.curselection()
        if not selection:
            return
        idx = selection[0]
        ordered = list(reversed(self.conversations))
        if idx < len(ordered):
            self.current_id = ordered[idx]["id"]
            self.render_conversation()

    def refresh_chat_list(self):
        self.chat_list.delete(0, "end")
        for c in reversed(self.conversations):
            title = c.get("title", "Conversation")
            self.chat_list.insert("end", title[:32])
        if self.current_id:
            for i, c in enumerate(reversed(self.conversations)):
                if c.get("id") == self.current_id:
                    self.chat_list.selection_set(i)
                    self.chat_list.see(i)
                    break

    def render_conversation(self):
        c = self.current_chat()
        if not c:
            return
        self.heading.config(text=c.get("title", "Conversation"))
        self.chat_text.config(state="normal")
        self.chat_text.delete("1.0", "end")
        for m in c.get("messages", []):
            role = m.get("role", "assistant")
            self.chat_text.insert("end", "You\n" if role == "user" else "CART3R AI\n",
                                  "user" if role == "user" else "assistant")
            self.chat_text.insert("end", m.get("content", "") + "\n\n", "body")
        self.chat_text.config(state="disabled")
        self.chat_text.see("end")
        self.refresh_chat_list()

    def append_message(self, role, content):
        c = self.current_chat()
        if not c:
            return
        c["messages"].append({"role": role, "content": content})
        c["updated"] = datetime.now().isoformat(timespec="seconds")
        if len(c["messages"]) == 1 and role == "user":
            c["title"] = content.strip().replace("\n", " ")[: thirty()] or "New conversation"
        self.persist()
        self.render_conversation()

    def persist(self):
        self.save_json(HISTORY_FILE, self.conversations)

    def send_message(self):
        if self.busy:
            return
        prompt = self.entry.get("1.0", "end").strip()
        if not prompt:
            return
        self.entry.delete("1.0", "end")
        self.append_message("user", prompt)
        self.busy = True
        self.send_btn.config(state="disabled", text="Thinking…")
        self.provider_label.config(text="CART3R AI is working…")
        threading.Thread(target=self._get_reply, daemon=True).start()

    def _get_reply(self):
        c = self.current_chat()
        messages = [{"role": "system", "content": self.settings.get("system_prompt", DEFAULTS["system_prompt"])}]
        if c:
            messages.extend(c.get("messages", [])[-30:])
        mode = self.settings.get("mode", "Auto (local first)")
        reply = None
        errors = []
        if mode in ("Auto (local first)", "Local only"):
            try:
                reply = self.call_ollama(messages)
            except Exception as e:
                errors.append("Local model: " + str(e))
                if mode == "Local only":
                    reply = "I couldn't reach Ollama. Make sure Ollama is running and the selected model is installed.\n\nDetails: " + str(e)
        if reply is None and mode in ("Auto (local first)", "Cloud only"):
            try:
                reply = self.call_cloud(messages)
            except Exception as e:
                errors.append("Cloud model: " + str(e))
                reply = "I couldn't get a response from the cloud provider.\n\n" + str(e)
        if reply is None:
            reply = "No AI provider is available. Start Ollama locally or configure a cloud API key in Settings.\n\n" + "\n".join(errors)
        self.root.after(0, lambda: self.finish_reply(reply))

    def call_ollama(self, messages):
        url = self.settings["ollama_url"].rstrip("/") + "/api/chat"
        payload = {"model": self.settings["ollama_model"], "messages": messages, "stream": False}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("message", {}).get("content", "The local model returned an empty response.")

    def call_cloud(self, messages):
        key = self.settings.get("api_key", "").strip() or os.getenv("CART3R_API_KEY", "").strip()
        if not key:
            raise RuntimeError("No cloud API key configured. Add one in Settings or set CART3R_API_KEY.")
        base = self.settings["cloud_url"].rstrip("/")
        url = base if base.endswith("/chat/completions") else base + "/chat/completions"
        payload = {"model": self.settings["cloud_model"], "messages": messages, "stream": False}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
             headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    def finish_reply(self, reply):
        self.append_message("assistant", reply)
        self.busy = False
        self.send_btn.config(state="normal", text="Send  ➤")
        self.provider_label.config(text=self.provider_status())

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("CART3R AI Settings")
        win.geometry("620x590")
        win.transient(self.root)
        win.grab_set()
        win.configure(bg="#f4f5f7")
        frame = tk.Frame(win, bg="#f4f5f7", padx=22, pady=18)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="AI ENGINE SETTINGS", bg="#f4f5f7", fg="#202633",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 12))
        vars = {}
        def field(label, key, show=None):
            tk.Label(frame, text=label, bg="#f4f5f7", fg="#424b59").pack(anchor="w", pady=(7, 2))
            v = tk.StringVar(value=str(self.settings.get(key, "")))
            e = ttk.Entry(frame, textvariable=v, show=show)
            e.pack(fill="x")
            vars[key] = v
        tk.Label(frame, text="Routing mode", bg="#f4f5f7", fg="#424b59").pack(anchor="w", pady=(5, 2))
        mode = tk.StringVar(value=self.settings.get("mode", DEFAULTS["mode"]))
        ttk.Combobox(frame, textvariable=mode, values=["Auto (local first)", "Local only", "Cloud only"],
                     state="readonly").pack(fill="x")
        field("Ollama URL", "ollama_url")
        field("Local model name", "ollama_model")
        field("Cloud API base URL (OpenAI-compatible)", "cloud_url")
        field("Cloud model name", "cloud_model")
        field("Cloud API key (stored in your Windows user profile)", "api_key", show="•")
        field("System instructions", "system_prompt")
        def save():
            self.settings["mode"] = mode.get()
            for k, v in vars.items():
                self.settings[k] = v.get().strip()
            self.save_json(CONFIG_FILE, self.settings)
            self.provider_label.config(text=self.provider_status())
            win.destroy()
            messagebox.showinfo("CART3R AI", "Settings saved.")
        ttk.Button(frame, text="Save settings", command=save).pack(anchor="e", pady=18)

    def delete_chat(self):
        c = self.current_chat()
        if not c:
            return
        if not messagebox.askyesno("Delete conversation", "Delete this conversation permanently?"):
            return
        self.conversations = [x for x in self.conversations if x.get("id") != self.current_id]
        self.current_id = self.conversations[-1]["id"] if self.conversations else None
        self.persist()
        if not self.current_id:
            self.new_chat()
        else:
            self.refresh_chat_list()
            self.render_conversation()

    def on_close(self):
        self.persist()
        self.root.destroy()

def thirty():
    return 30

if __name__ == "__main__":
    APP_DIR.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    app = Cart3rApp(root)
    root.mainloop()
