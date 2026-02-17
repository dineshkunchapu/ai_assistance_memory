# ============================================================
#   AI Assistant with Memory
#   Author : Dinesh Kunchapu
#   Stack  : Python + Streamlit + Anthropic Claude API
#   Run    : streamlit run app.py
# ============================================================

import streamlit as st
import json
import os
import re
import requests
from datetime import datetime
from typing import List, Dict, Optional

# ──────────────────────────────────────────────────────────────
#  MEMORY MANAGER  (unchanged — works perfectly)
# ──────────────────────────────────────────────────────────────
class MemoryManager:
    IMPORTANT_KEYWORDS = [
        'remember', 'important', 'prefer', 'always', 'never',
        'my name is', 'i am', 'i work', 'i like', 'i need',
        'i prefer', 'i use', 'i study', 'i want', 'i hate',
        'call me', 'i\'m from', 'i live'
    ]

    def __init__(self, memory_file: str = "memory_store.json"):
        self.memory_file    = memory_file
        self.short_term     = []
        self.long_term      = []
        self.context_window = 10
        self._load()

    def add(self, content: str, kind: str, meta: Optional[Dict] = None):
        item = {
            "content"  : content,
            "type"     : kind,
            "timestamp": datetime.now().isoformat(),
            "metadata" : meta or {}
        }
        self.short_term.append(item)
        if self._is_important(content):
            self.long_term.append(item)
            self._save()
        cap = self.context_window * 2
        if len(self.short_term) > cap:
            self.short_term = self.short_term[-cap:]

    def relevant(self, query: str, top_k: int = 5) -> List[Dict]:
        qw = set(query.lower().split())
        scored = sorted(
            [{"m": m, "s": len(qw & set(m["content"].lower().split()))}
             for m in self.long_term],
            key=lambda x: x["s"], reverse=True
        )
        return [x["m"] for x in scored if x["s"] > 0][:top_k]

    def all_memories(self) -> List[Dict]:
        return self.long_term

    def count(self) -> int:
        return len(self.short_term) + len(self.long_term)

    def save_session(self, session_id: str, messages: List[Dict]):
        os.makedirs("sessions", exist_ok=True)
        try:
            with open(f"sessions/session_{session_id}.json", "w") as f:
                json.dump({"session_id": session_id, "messages": messages,
                           "timestamp": datetime.now().isoformat()}, f, indent=2)
        except Exception as e:
            print(f"Session save error: {e}")

    def memory_context_string(self) -> str:
        """Build a string of long-term memories to inject into AI prompt"""
        if not self.long_term:
            return ""
        lines = [f"- {m['content']}" for m in self.long_term[-10:]]
        return "Things I remember about this user:\n" + "\n".join(lines)

    def _is_important(self, text: str) -> bool:
        t = text.lower()
        return any(kw in t for kw in self.IMPORTANT_KEYWORDS)

    def _save(self):
        try:
            with open(self.memory_file, "w") as f:
                json.dump({"long_term": self.long_term,
                           "updated": datetime.now().isoformat()}, f, indent=2)
        except Exception as e:
            print(f"Memory save error: {e}")

    def _load(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file) as f:
                    self.long_term = json.load(f).get("long_term", [])
        except Exception as e:
            print(f"Memory load error: {e}")
            self.long_term = []


# ──────────────────────────────────────────────────────────────
#  AI RESPONSE  — uses Claude API for real intelligence
# ──────────────────────────────────────────────────────────────
def get_ai_response(user_input: str, chat_history: List[Dict],
                    mem: MemoryManager, profile: Dict, api_key: str) -> str:
    """Call Gemini API with full conversation history + memory context."""

    name = profile.get("name", "")
    memory_ctx = mem.memory_context_string()

    system_prompt = f"""You are a helpful, friendly AI assistant with memory capabilities.
You remember things users tell you and use that context in your replies.
Keep responses conversational, clear, and genuinely useful.
Be concise but thorough. Sound like a knowledgeable friend, not a textbook.
{"The user's name is " + name + "." if name else ""}
{memory_ctx}
You specialize in: Python, Machine Learning, Data Science, AI, and career/placement guidance.
When answering technical questions, give real explanations with examples.
When the user says things like "remember that..." or "my name is..." — acknowledge you've stored it."""

    # Build Gemini contents array (user/model turns)
    contents = []
    history = [m for m in chat_history[-20:] if m["role"] in ("user", "assistant")]
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # ensure last turn is user
    if not contents or contents[-1]["role"] != "user":
        contents.append({"role": "user", "parts": [{"text": user_input}]})

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": contents,
                "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.7}
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        elif response.status_code == 400:
            return "❌ Invalid API key. Check your Gemini key."
        elif response.status_code == 429:
            return "⚠️ Rate limit hit. Wait a moment and try again."
        else:
            return f"⚠️ API error {response.status_code}: {response.text[:200]}"

    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. Check your internet and try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ──────────────────────────────────────────────────────────────
#  EXPORT UTILITY
# ──────────────────────────────────────────────────────────────
def export_conversation(messages: List[Dict], session_id: str, fmt: str) -> str:
    if fmt == "json":
        return json.dumps({"session_id": session_id,
                           "exported": datetime.now().isoformat(),
                           "messages": messages}, indent=2)
    if fmt == "text":
        lines = [f"AI Assistant Conversation — {session_id}\n{'='*50}"]
        for m in messages:
            lines.append(f"\n[{m['role'].upper()}] {m.get('timestamp','')}\n{m['content']}")
        return "\n".join(lines)
    # markdown default
    lines = [f"# AI Assistant Conversation\n**Session:** {session_id}  \n**Date:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n"]
    for m in messages:
        icon = "👤" if m["role"] == "user" else "🤖"
        lines.append(f"### {icon} {m['role'].capitalize()}  \n_{m.get('timestamp','')}_\n\n{m['content']}\n\n---\n")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
#  STREAMLIT APP
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Assistant with Memory",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── init session state ────────────────────────────────────────
def _init():
    if "ready" not in st.session_state:
        st.session_state.ready      = True
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages   = []
        st.session_state.mem        = MemoryManager()
        st.session_state.profile    = {"name": "", "preferences": {}}
        st.session_state.exchanges  = 0
        st.session_state.started    = datetime.now()
        st.session_state.api_key    = "AIzaSyAJz-UYM0yyyoB8Ub4-DZXVl8LmkQuAe9g"

_init()

# ── sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 Control Panel")

    # ── API KEY INPUT ──
    st.subheader("🔑 API Key")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="AIza...",
        help="Get your FREE key at aistudio.google.com/apikey"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    if st.session_state.api_key:
        st.success("✅ Gemini API key set — ready to chat!")
    else:
        st.warning("⚠️ Enter API key to enable AI responses")
        st.markdown("[Get FREE Gemini key →](https://aistudio.google.com/apikey)", unsafe_allow_html=False)

    st.divider()

    # ── User Profile ──
    with st.expander("👤 User Profile", expanded=False):
        name = st.text_input("Your Name", value=st.session_state.profile["name"])
        if name:
            st.session_state.profile["name"] = name
        st.caption(f"Session: `{st.session_state.session_id}`")
        st.caption(f"Started: {st.session_state.started:%H:%M:%S}")

    # ── Memory Stats ──
    with st.expander("📊 Memory Stats", expanded=True):
        c1, c2 = st.columns(2)
        c1.metric("Messages",  len(st.session_state.messages))
        c2.metric("Exchanges", st.session_state.exchanges)
        mc = st.session_state.mem.count()
        st.metric("Memory Items", mc)
        if mc:
            st.progress(min(mc / 50, 1.0))
            st.caption(f"{mc} / 50 slots used")

    st.divider()

    # ── Session controls ──
    st.subheader("💾 Session")
    c1, c2 = st.columns(2)
    if c1.button("🗑️ Clear", use_container_width=True):
        st.session_state.messages  = []
        st.session_state.exchanges = 0
        st.rerun()

    if c2.button("🔄 New", use_container_width=True):
        if st.session_state.messages:
            st.session_state.mem.save_session(
                st.session_state.session_id, st.session_state.messages)
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages   = []
        st.session_state.exchanges  = 0
        st.session_state.started    = datetime.now()
        st.rerun()

    # ── Export ──
    st.subheader("📤 Export")
    if st.session_state.messages:
        fmt  = st.selectbox("Format", ["Markdown", "JSON", "Text"], label_visibility="collapsed")
        ext  = {"Markdown": "md", "JSON": "json", "Text": "txt"}[fmt]
        mime = "application/json" if fmt == "JSON" else "text/plain"
        data = export_conversation(st.session_state.messages,
                                   st.session_state.session_id, fmt.lower())
        st.download_button(f"⬇️ Download {fmt}", data=data,
                           file_name=f"chat_{st.session_state.session_id}.{ext}",
                           mime=mime, use_container_width=True)
    else:
        st.caption("No messages to export yet.")

    st.divider()

    # ── Memory Browser ──
    with st.expander("🧠 Memory Browser", expanded=False):
        mems = st.session_state.mem.all_memories()
        if mems:
            for i, m in enumerate(mems[-5:], 1):
                st.markdown(f"**{i}.** {m['content'][:60]}…")
                st.caption(f"{m['type']} · {m['timestamp'][:10]}")
        else:
            st.info("No memories stored yet.")

# ── main area ─────────────────────────────────────────────────
st.title("🤖 AI Assistant with Memory")
st.caption("Powered by Claude AI · Remembers your preferences · Built by Dinesh Kunchapu")
st.divider()

# No API key — show setup instructions
if not st.session_state.api_key:
    st.info("👈 Enter your Anthropic API key in the sidebar to start chatting.")

    with st.expander("📖 How to get a free API key", expanded=True):
        st.markdown("""
        1. Go to **[aistudio.google.com/apikey](https://aistudio.google.com/apikey)**
        2. Sign up for a free account
        3. Click **API Keys** → **Create Key**
        4. Copy the key (starts with `AIza...`)
        5. Paste it in the sidebar 👈

        **Completely free — no credit card needed!**
        """)
    st.stop()

# Welcome screen
if not st.session_state.messages:
    st.markdown("""
### Welcome! 👋
I'm an AI assistant powered by Claude that **remembers** your preferences across conversations.

**Try saying:**
- `My name is Dinesh`
- `I'm a final year CSE student preparing for placements`
- `Explain how random forests work`
- `What do you know about me?`
- `Help me prepare for a data science interview`
""")
    st.divider()

# ── render chat history ───────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        st.caption(msg.get("timestamp", ""))

# ── chat input ────────────────────────────────────────────────
if prompt := st.chat_input("Type your message here…"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # store & show user message
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": ts})
    st.session_state.exchanges += 1
    st.session_state.mem.add(prompt, "user_input", {"timestamp": ts})

    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(ts)

    # generate & show AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply = get_ai_response(
                prompt,
                st.session_state.messages,
                st.session_state.mem,
                st.session_state.profile,
                st.session_state.api_key
            )
        st.markdown(reply)
        rts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(rts)

    # store assistant message + memory
    st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": rts})
    st.session_state.mem.add(reply, "assistant_response", {"timestamp": rts})