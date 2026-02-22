"""
RealAI GUI Launcher

A graphical interface for configuring API keys and launching the RealAI API
server.  Runs on Windows, macOS, and Linux (requires tkinter, which ships with
the official Python installer on Windows and macOS).

Usage
-----
Run directly::

    python realai_gui.py

Build a Windows .exe::

    pip install pyinstaller
    pyinstaller realai_launcher.spec
    # Output: dist/RealAI.exe
"""

import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Optional

from realai import PROVIDER_ENV_VARS

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".realai")
_CONFIG_FILE = os.path.join(_CONFIG_DIR, "config.json")

#: Ordered list of providers shown in the UI.
#: ``env_var`` values are sourced from :data:`realai.PROVIDER_ENV_VARS`.
PROVIDERS = {
    "openai": {
        "label": "OpenAI",
        "placeholder": "sk-...",
        "help": "Get your key at https://platform.openai.com/api-keys",
        "env_var": PROVIDER_ENV_VARS["openai"],
    },
    "anthropic": {
        "label": "Anthropic (Claude)",
        "placeholder": "sk-ant-...",
        "help": "Get your key at https://console.anthropic.com/",
        "env_var": PROVIDER_ENV_VARS["anthropic"],
    },
    "grok": {
        "label": "xAI / Grok",
        "placeholder": "xai-...",
        "help": "Get your key at https://console.x.ai/",
        "env_var": PROVIDER_ENV_VARS["grok"],
    },
    "gemini": {
        "label": "Google Gemini",
        "placeholder": "AIza...",
        "help": "Get your key at https://aistudio.google.com/app/apikey",
        "env_var": PROVIDER_ENV_VARS["gemini"],
    },
}


def load_config() -> dict:
    """Load saved API keys from ``~/.realai/config.json``."""
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_config(config: dict) -> None:
    """Persist API keys to ``~/.realai/config.json``."""
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class RealAILauncher(tk.Tk):
    """Main GUI window for RealAI API key configuration and server control."""

    _HEADER_BG = "#1a1a2e"
    _HEADER_FG = "#e0e0ff"
    _HEADER_SUB = "#9090cc"
    _BTN_SAVE = "#2a7a4f"
    _BTN_START = "#1565c0"
    _BTN_STOP = "#c62828"
    _PAD = 14

    def __init__(self):
        super().__init__()
        self.title("RealAI v2.0 \u2014 API Key Setup")
        self.resizable(False, False)
        self._server_proc: Optional[subprocess.Popen] = None
        self._entries: Dict[str, tk.Entry] = {}
        self._build_ui()
        self._load_saved_keys()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        pad = self._PAD

        # Header bar
        header = tk.Frame(self, bg=self._HEADER_BG)
        header.grid(row=0, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)
        tk.Label(
            header,
            text="\U0001f916  RealAI v2.0",
            font=("Segoe UI", 18, "bold"),
            bg=self._HEADER_BG,
            fg=self._HEADER_FG,
            pady=12,
        ).pack()
        tk.Label(
            header,
            text="Enter your API keys below \u2014 they are saved locally, never uploaded",
            font=("Segoe UI", 9),
            bg=self._HEADER_BG,
            fg=self._HEADER_SUB,
            pady=2,
        ).pack()

        # API key form
        form = tk.Frame(self, padx=pad, pady=pad)
        form.grid(row=1, column=0, sticky="nsew")
        form.columnconfigure(0, weight=1)

        for row_idx, (provider_id, info) in enumerate(PROVIDERS.items()):
            base = row_idx * 3

            # Label
            tk.Label(
                form,
                text=f"{info['label']} API Key",
                font=("Segoe UI", 10, "bold"),
                anchor="w",
            ).grid(row=base, column=0, columnspan=2, sticky="w", pady=(pad // 2, 0))

            # Password entry
            entry = tk.Entry(form, width=50, show="\u2022", font=("Consolas", 10))
            entry.grid(row=base + 1, column=0, sticky="ew", padx=(0, 6), pady=(2, 0))
            self._entries[provider_id] = entry

            # Eye toggle
            def _make_toggle(e: tk.Entry = entry) -> Callable[[], None]:
                def _toggle() -> None:
                    e.config(show="" if e.cget("show") else "\u2022")
                return _toggle

            tk.Button(
                form,
                text="\U0001f441",
                width=3,
                command=_make_toggle(),
                relief="flat",
                cursor="hand2",
            ).grid(row=base + 1, column=1, pady=(2, 0))

            # Help text
            tk.Label(
                form,
                text=info["help"],
                font=("Segoe UI", 8),
                fg="#777",
                anchor="w",
            ).grid(row=base + 2, column=0, columnspan=2, sticky="w")

        # Status bar
        self._status_var = tk.StringVar(value="Ready \u2014 enter your API keys above.")
        tk.Label(
            self,
            textvariable=self._status_var,
            font=("Segoe UI", 9),
            fg="#555",
            anchor="w",
            padx=pad,
            pady=4,
        ).grid(row=2, column=0, sticky="ew")

        # Button row
        btn_row = tk.Frame(self, padx=pad, pady=pad // 2)
        btn_row.grid(row=3, column=0, sticky="ew")

        tk.Button(
            btn_row,
            text="\U0001f4be  Save Keys",
            width=14,
            font=("Segoe UI", 10),
            bg=self._BTN_SAVE,
            fg="white",
            activebackground="#1f5a39",
            relief="flat",
            cursor="hand2",
            command=self._save_keys,
        ).pack(side="left", padx=(0, 8))

        self._server_btn = tk.Button(
            btn_row,
            text="\U0001f680  Start API Server",
            width=18,
            font=("Segoe UI", 10),
            bg=self._BTN_START,
            fg="white",
            activebackground="#0d47a1",
            relief="flat",
            cursor="hand2",
            command=self._toggle_server,
        )
        self._server_btn.pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row,
            text="\u2716  Clear All",
            width=10,
            font=("Segoe UI", 10),
            bg=self._BTN_STOP,
            fg="white",
            activebackground="#8b0000",
            relief="flat",
            cursor="hand2",
            command=self._clear_keys,
        ).pack(side="right")

    # ------------------------------------------------------------------
    # Key management
    # ------------------------------------------------------------------

    def _load_saved_keys(self) -> None:
        """Populate entry fields from the saved config file."""
        config = load_config()
        for provider_id, entry in self._entries.items():
            value = config.get(provider_id, "")
            if value:
                entry.delete(0, tk.END)
                entry.insert(0, value)
        configured = [p for p in PROVIDERS if config.get(p)]
        if configured:
            names = ", ".join(PROVIDERS[p]["label"] for p in configured)
            self._status_var.set(f"Loaded saved keys for: {names}")

    def _save_keys(self) -> None:
        """Write the current entry values to disk and apply them as env vars."""
        config = {pid: entry.get().strip() for pid, entry in self._entries.items()}
        save_config(config)

        # Apply to the current process environment so a server subprocess inherits them.
        for provider_id, key in config.items():
            env_var = PROVIDERS[provider_id]["env_var"]
            if key:
                os.environ[env_var] = key
            else:
                os.environ.pop(env_var, None)

        configured = [p for p, v in config.items() if v]
        if configured:
            names = ", ".join(PROVIDERS[p]["label"] for p in configured)
            self._status_var.set(f"\u2705 Saved keys for: {names}")
        else:
            self._status_var.set("\u2705 Saved (no keys — RealAI runs in placeholder mode).")

    def _clear_keys(self) -> None:
        for entry in self._entries.values():
            entry.delete(0, tk.END)
        self._status_var.set("Keys cleared \u2014 click Save to persist.")

    # ------------------------------------------------------------------
    # Server control
    # ------------------------------------------------------------------

    def _toggle_server(self) -> None:
        if self._server_proc and self._server_proc.poll() is None:
            self._stop_server()
        else:
            self._start_server()

    def _start_server(self) -> None:
        """Save keys, then launch api_server.py in a subprocess."""
        self._save_keys()
        server_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "api_server.py"
        )
        # Build child env inheriting the updated os.environ (which now has API keys).
        try:
            self._server_proc = subprocess.Popen(
                [sys.executable, server_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except Exception as exc:
            messagebox.showerror("Server Error", f"Could not start server:\n{exc}")
            return

        self._server_btn.config(
            text="\u23f9  Stop API Server",
            bg=self._BTN_STOP,
            activebackground="#8b0000",
        )
        self._status_var.set("\U0001f680 API server started \u2014 http://localhost:8000")
        threading.Thread(target=self._monitor_server, daemon=True).start()

    def _stop_server(self) -> None:
        if self._server_proc:
            self._server_proc.terminate()
            self._server_proc = None
        self._server_btn.config(
            text="\U0001f680  Start API Server",
            bg=self._BTN_START,
            activebackground="#0d47a1",
        )
        self._status_var.set("\u23f9 API server stopped.")

    def _monitor_server(self) -> None:
        """Background thread: update the button when the server exits on its own."""
        if self._server_proc:
            self._server_proc.wait()
            self.after(0, self._on_server_exit)

    def _on_server_exit(self) -> None:
        self._server_proc = None
        self._server_btn.config(
            text="\U0001f680  Start API Server",
            bg=self._BTN_START,
            activebackground="#0d47a1",
        )
        self._status_var.set("\u26a0\ufe0f API server exited unexpectedly.")

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        if self._server_proc and self._server_proc.poll() is None:
            self._stop_server()
        self.destroy()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app = RealAILauncher()
    app.mainloop()


if __name__ == "__main__":
    main()
