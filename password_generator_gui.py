import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

AMBIGUOUS_CHARS = "0O1lI"

STRENGTH_COLORS = {
    "Weak": "#ef4444",
    "Medium": "#f59e0b",
    "Strong": "#22c55e",
}



def build_pool(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    pool = ""
    if use_upper:
        pool += string.ascii_uppercase
    if use_lower:
        pool += string.ascii_lowercase
    if use_digits:
        pool += string.digits
    if use_symbols:
        pool += string.punctuation

    if exclude_ambiguous:
        pool = "".join(ch for ch in pool if ch not in AMBIGUOUS_CHARS)

    return pool


def generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    def clean(chars):
        if exclude_ambiguous:
            return "".join(ch for ch in chars if ch not in AMBIGUOUS_CHARS)
        return chars

    pool = build_pool(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)
    if not pool:
        raise ValueError("No character types selected.")

  
    guaranteed = []
    if use_upper:
        guaranteed.append(secrets.choice(clean(string.ascii_uppercase) or string.ascii_uppercase))
    if use_lower:
        guaranteed.append(secrets.choice(clean(string.ascii_lowercase) or string.ascii_lowercase))
    if use_digits:
        guaranteed.append(secrets.choice(clean(string.digits) or string.digits))
    if use_symbols:
        guaranteed.append(secrets.choice(clean(string.punctuation) or string.punctuation))

    remaining = length - len(guaranteed)
    rest = [secrets.choice(pool) for _ in range(max(remaining, 0))]

    chars = guaranteed + rest
    
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]

    return "".join(chars[:length]) if len(chars) > length else "".join(chars)


def evaluate_strength(password, type_count):
    """Simple strength heuristic based on length and character diversity."""
    length = len(password)
    if length >= 14 and type_count >= 3:
        return "Strong"
    elif length >= 10 and type_count >= 2:
        return "Medium"
    else:
        return "Weak"




class PasswordGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator — Advanced")
        self.geometry("460x620")
        self.configure(bg="#0f1117")
        self.resizable(False, False)

        self.history = []  # in-session only, never written to disk

        self._build_styles()
        self._build_widgets()

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", background="#0f1117", foreground="#e8e9ee", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TCheckbutton", background="#0f1117", foreground="#e8e9ee", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Horizontal.TScale", background="#0f1117")

    def _build_widgets(self):
        ttk.Label(self, text="Password Generator", style="Header.TLabel").pack(pady=(20, 4))
        ttk.Label(self, text="Cryptographically secure, with strength feedback").pack(pady=(0, 16))

        
        length_frame = tk.Frame(self, bg="#0f1117")
        length_frame.pack(fill="x", padx=24, pady=6)
        ttk.Label(length_frame, text="Password length:").pack(anchor="w")

        self.length_var = tk.IntVar(value=16)
        self.length_display = ttk.Label(length_frame, text="16")
        self.length_display.pack(anchor="e")

        self.length_slider = ttk.Scale(
            length_frame, from_=8, to=64, orient="horizontal",
            variable=self.length_var, command=self._on_length_change
        )
        self.length_slider.pack(fill="x")

        options_frame = tk.Frame(self, bg="#0f1117")
        options_frame.pack(fill="x", padx=24, pady=12)

        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=self.upper_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=self.lower_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Numbers (0-9)", variable=self.digits_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Symbols (!@#$...)", variable=self.symbols_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(
            options_frame, text="Exclude ambiguous characters (0, O, 1, l, I)",
            variable=self.ambiguous_var
        ).pack(anchor="w", pady=(10, 2))

        ttk.Button(self, text="Generate Password", command=self.on_generate).pack(pady=14)

        result_frame = tk.Frame(self, bg="#1f2330")
        result_frame.pack(fill="x", padx=24, pady=4)

        self.password_var = tk.StringVar(value="")
        password_entry = tk.Entry(
            result_frame, textvariable=self.password_var, font=("Consolas", 13),
            bg="#1f2330", fg="#e8e9ee", relief="flat", justify="center", state="readonly"
        )
        password_entry.pack(fill="x", padx=10, pady=10)

      
        self.strength_label = ttk.Label(self, text="", font=("Segoe UI", 10, "bold"))
        self.strength_label.pack(pady=(4, 0))

        self.strength_bar = tk.Frame(self, bg="#1f2330", height=8)
        self.strength_bar.pack(fill="x", padx=24, pady=(4, 12))
        self.strength_fill = tk.Frame(self.strength_bar, bg="#1f2330", height=8, width=0)
        self.strength_fill.place(x=0, y=0)

        ttk.Button(self, text="📋 Copy to Clipboard", command=self.on_copy).pack(pady=4)

        ttk.Label(self, text="Recent passwords (this session only):").pack(anchor="w", padx=24, pady=(16, 4))
        self.history_box = tk.Listbox(
            self, bg="#171a23", fg="#9598a8", font=("Consolas", 9),
            relief="flat", height=5, highlightthickness=0
        )
        self.history_box.pack(fill="x", padx=24, pady=(0, 12))

    def _on_length_change(self, value):
        self.length_display.configure(text=str(int(float(value))))

    def on_generate(self):
        length = int(self.length_var.get())
        use_upper = self.upper_var.get()
        use_lower = self.lower_var.get()
        use_digits = self.digits_var.get()
        use_symbols = self.symbols_var.get()
        exclude_ambiguous = self.ambiguous_var.get()

        type_count = sum([use_upper, use_lower, use_digits, use_symbols])
        if type_count == 0:
            messagebox.showwarning("No character types", "Please select at least one character type.")
            return

        try:
            password = generate_password(
                length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous
            )
        except ValueError as e:
            messagebox.showwarning("Invalid selection", str(e))
            return

        self.password_var.set(password)

        strength = evaluate_strength(password, type_count)
        self.strength_label.configure(text=f"Strength: {strength}", foreground=STRENGTH_COLORS[strength])
        fill_ratio = {"Weak": 0.33, "Medium": 0.66, "Strong": 1.0}[strength]
        bar_width = int(412 * fill_ratio)
        self.strength_fill.configure(bg=STRENGTH_COLORS[strength], width=bar_width)

        self.history.insert(0, password)
        self.history = self.history[:5]
        self.history_box.delete(0, tk.END)
        for pw in self.history:
            self.history_box.insert(tk.END, pw)

        self._copy_to_clipboard(password, silent=True)

    def on_copy(self):
        password = self.password_var.get()
        if not password:
            messagebox.showinfo("Nothing to copy", "Generate a password first.")
            return
        self._copy_to_clipboard(password, silent=False)

    def _copy_to_clipboard(self, text, silent=False):
        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(text)
                if not silent:
                    messagebox.showinfo("Copied", "Password copied to clipboard.")
            except Exception:
                if not silent:
                    messagebox.showwarning("Clipboard error", "Could not access the clipboard.")
        else:
            
            self.clipboard_clear()
            self.clipboard_append(text)
            if not silent:
                messagebox.showinfo("Copied", "Password copied to clipboard.")


if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
