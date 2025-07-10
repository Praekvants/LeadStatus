# ---------- Reply / Bounce cleaner for influencer CSVs ----------
from __future__ import annotations   # ✅ supports 3.7-3.11
import os, pandas as pd, tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
from typing import Optional

# ── CONFIG ────────────────────────────────────────────────────── #
KEEP_STATUSES = {
    "Completed | Contacted",
    "Completed | Email opened but no reply",
    "Completed | Not yet contacted",
}
STATUS_COL_PRIORITY = ("Lead status",)        # fallback: first col with 'status'
OUT_FOLDER_NAME     = "Cleaned_NoReplies"     # appears on Desktop
# ──────────────────────────────────────────────────────────────── #

def _detect_status_column(df: pd.DataFrame) -> Optional[str]:
    """Return the most likely status column."""
    for col in STATUS_COL_PRIORITY:
        if col in df.columns:
            return col
    for col in df.columns:
        if "status" in str(col).lower():
            return col
    return None

def clean_csv(path: str, out_dir: str | None = None) -> None:
    df = pd.read_csv(path)

    col = _detect_status_column(df)
    if not col:
        print(f"⚠️  No status column in {os.path.basename(path)} – skipped")
        return

    keep_mask = df[col].astype(str).str.strip().isin(KEEP_STATUSES)
    cleaned   = df.loc[keep_mask]

    if out_dir is None:
        out_dir = os.path.join(os.path.expanduser("~"), "Desktop", OUT_FOLDER_NAME)
    os.makedirs(out_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(path))[0]
    out_file = os.path.join(out_dir, f"{base}_clean.csv")
    cleaned.to_csv(out_file, index=False)
    print("✓ saved", out_file)

class ReplyCleaner(TkinterDnD.Tk):
    """Drag-and-drop GUI for removing rows with unwanted Lead statuses."""
    def __init__(self):
        super().__init__()
        self.title("Lead-Status Filter")
        self.geometry("600x280")
        self.configure(bg="#001f3f")

        lbl = tk.Label(
            self,
            text="Drag CSV file(s) here\n(keeps only the 3 allowed statuses)",
            bg="#001f3f",
            fg="white",
            font=("Helvetica", 16),
            justify="center",
        )
        lbl.pack(expand=True, fill="both")
        lbl.drop_target_register(DND_FILES)
        lbl.dnd_bind("<<Drop>>", lambda e: self._run(self.tk.splitlist(e.data)))

        tk.Button(self, text="Browse", command=self._browse,
                  bg="#001f3f", fg="white").pack(pady=6)

    # helpers ─────────────────────────────────────────────────── #
    def _browse(self):
        files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        self._run(files)

    def _run(self, paths):
        for p in paths:
            clean_csv(p)

if __name__ == "__main__":
    ReplyCleaner().mainloop()
