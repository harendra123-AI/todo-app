import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")

BG = "#1e1e2e"
SURFACE = "#313244"
ACCENT = "#cba6f7"
TEXT = "#cdd6f4"
SUBTEXT = "#a6adc8"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
BORDER = "#45475a"


def load_todos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_todos(todos):
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, indent=2)


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do")
        self.geometry("520x620")
        self.minsize(400, 500)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.todos = load_todos()
        self.filter_var = tk.StringVar(value="All")

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG, pady=16)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="My To-Do List", font=("Segoe UI", 20, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")

        # Input row
        inp = tk.Frame(self, bg=BG)
        inp.pack(fill="x", padx=20, pady=(0, 12))

        self.entry = tk.Entry(inp, font=("Segoe UI", 13), bg=SURFACE, fg=TEXT,
                              insertbackground=TEXT, relief="flat",
                              highlightthickness=1, highlightbackground=BORDER,
                              highlightcolor=ACCENT)
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self._add_task())

        tk.Button(inp, text="Add", font=("Segoe UI", 12, "bold"),
                  bg=ACCENT, fg=BG, activebackground="#b4befe", relief="flat",
                  cursor="hand2", padx=14, pady=6,
                  command=self._add_task).pack(side="left")

        # Filter row
        flt = tk.Frame(self, bg=BG)
        flt.pack(fill="x", padx=20, pady=(0, 10))
        for label in ("All", "Active", "Done"):
            tk.Radiobutton(flt, text=label, variable=self.filter_var, value=label,
                           font=("Segoe UI", 10), bg=BG, fg=SUBTEXT,
                           selectcolor=BG, activebackground=BG,
                           activeforeground=ACCENT,
                           indicatoron=False, relief="flat", padx=10, pady=4,
                           cursor="hand2",
                           command=self._refresh_list).pack(side="left", padx=2)

        # Separator
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 8))

        # Task list (scrollable)
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.list_frame = tk.Frame(canvas, bg=BG)

        self.list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # Footer
        self.footer_var = tk.StringVar()
        tk.Label(self, textvariable=self.footer_var, font=("Segoe UI", 9),
                 bg=BG, fg=SUBTEXT).pack(pady=8)

    def _add_task(self):
        text = self.entry.get().strip()
        if not text:
            return
        task = {
            "id": int(datetime.now().timestamp() * 1000),
            "text": text,
            "done": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.todos.insert(0, task)
        save_todos(self.todos)
        self.entry.delete(0, tk.END)
        self._refresh_list()

    def _toggle_done(self, task_id):
        for t in self.todos:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                break
        save_todos(self.todos)
        self._refresh_list()

    def _delete_task(self, task_id):
        self.todos = [t for t in self.todos if t["id"] != task_id]
        save_todos(self.todos)
        self._refresh_list()

    def _clear_done(self):
        done_count = sum(1 for t in self.todos if t["done"])
        if done_count == 0:
            return
        if messagebox.askyesno("Clear done", f"Remove {done_count} completed task(s)?"):
            self.todos = [t for t in self.todos if not t["done"]]
            save_todos(self.todos)
            self._refresh_list()

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        f = self.filter_var.get()
        visible = [t for t in self.todos if
                   f == "All" or
                   (f == "Active" and not t["done"]) or
                   (f == "Done" and t["done"])]

        if not visible:
            tk.Label(self.list_frame, text="No tasks here.", font=("Segoe UI", 12),
                     bg=BG, fg=SUBTEXT).pack(pady=30)
        else:
            for task in visible:
                self._build_task_row(task)

        active = sum(1 for t in self.todos if not t["done"])
        done = sum(1 for t in self.todos if t["done"])
        self.footer_var.set(f"{active} remaining  •  {done} done")

        # Show clear-done button only when there are completed tasks
        for w in self.list_frame.winfo_children():
            pass  # already rebuilt

        if done > 0:
            tk.Button(self.list_frame, text="Clear completed",
                      font=("Segoe UI", 9), bg=SURFACE, fg=RED,
                      activebackground=BORDER, relief="flat", cursor="hand2",
                      pady=4, padx=10, command=self._clear_done
                      ).pack(pady=(12, 4))

    def _build_task_row(self, task):
        row = tk.Frame(self.list_frame, bg=SURFACE, pady=6, padx=10)
        row.pack(fill="x", pady=3)

        # Checkbox
        done_var = tk.BooleanVar(value=task["done"])
        cb = tk.Checkbutton(row, variable=done_var, bg=SURFACE,
                            activebackground=SURFACE,
                            command=lambda tid=task["id"]: self._toggle_done(tid),
                            cursor="hand2")
        cb.pack(side="left")

        # Task text
        style = ("Segoe UI", 12)
        color = SUBTEXT if task["done"] else TEXT
        lbl = tk.Label(row, text=task["text"], font=style, bg=SURFACE, fg=color,
                       wraplength=340, justify="left", anchor="w")
        if task["done"]:
            lbl.configure(font=("Segoe UI", 12, "overstrike"))
        lbl.pack(side="left", fill="x", expand=True, padx=6)

        # Delete button
        tk.Button(row, text="✕", font=("Segoe UI", 10), bg=SURFACE, fg=RED,
                  activebackground=BORDER, relief="flat", cursor="hand2",
                  padx=6, pady=2,
                  command=lambda tid=task["id"]: self._delete_task(tid)
                  ).pack(side="right")


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
