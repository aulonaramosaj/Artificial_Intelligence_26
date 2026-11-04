"""
Uninformed Search – graphical interface (Tkinter)
=================================================

One window, three tabs. Every tab calls the solvers from the task folders,
so the algorithms are exactly the same as in the console programs:

  1. Social Golfers   -> 1_social_golfers/social_golfers.py      (DFS + backtracking)
  2. Sudoku           -> 2_sudoku/sudoku_bfs.py                  (BFS + backtracking)
  3. Latin Square     -> 3_latin_square/latin_square_iddfs.py    (IDDFS + backtracking)

Solvers run in a background thread, so the window never freezes.

Run:  python3 app.py
"""

import colorsys
import os
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

HERE = os.path.dirname(os.path.abspath(__file__))
for folder in ("1_social_golfers", "2_sudoku", "3_latin_square"):
    sys.path.insert(0, os.path.join(HERE, folder))

import social_golfers as sg                                    # noqa: E402
import sudoku_bfs as sd                                        # noqa: E402
import latin_square_iddfs as ls                                # noqa: E402

BG = "#ffffff"
FG = "#1d1d1f"
BLUE = "#1f5fbf"
HILITE = "#ffe680"
PAD = 8


def text_widget(parent, height=10, width=40):
    frame = ttk.Frame(parent)
    t = tk.Text(frame, height=height, width=width, wrap="none", bg=BG, fg=FG,
                font=("Menlo", 11), relief="solid", borderwidth=1, insertbackground=FG)
    sy = ttk.Scrollbar(frame, orient="vertical", command=t.yview)
    sx = ttk.Scrollbar(frame, orient="horizontal", command=t.xview)
    t.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
    t.grid(row=0, column=0, sticky="nsew")
    sy.grid(row=0, column=1, sticky="ns")
    sx.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    t.configure(state="disabled")
    return frame, t


def write(t, text, append=False):
    t.configure(state="normal")
    if not append:
        t.delete("1.0", "end")
    t.insert("end", text)
    t.see("end")
    t.configure(state="disabled")


class App:
    def __init__(self, root):
        self.root = root
        root.title("Kërkimi i painformuar – Detyra 1")
        root.geometry("1280x820")
        root.minsize(1000, 650)
        self.q = queue.Queue()
        root.after(40, self._poll)

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        self.tabs = []
        for title, cls in (("1. Social Golfers (DFS)", GolfersTab),
                           ("2. Sudoku (BFS)", SudokuTab),
                           ("3. Latin Square (IDDFS)", LatinTab)):
            frame = ttk.Frame(nb, padding=PAD)
            nb.add(frame, text=title)
            self.tabs.append(cls(self, frame))

    # thread -> GUI messages (Tk widgets may only be touched by the main thread)
    def post(self, fn, *args):
        self.q.put((fn, args))

    def _poll(self):
        try:
            while True:
                fn, args = self.q.get_nowait()
                fn(*args)
        except queue.Empty:
            pass
        self.root.after(40, self._poll)

    def run_bg(self, fn):
        threading.Thread(target=fn, daemon=True).start()


# =========================================================== 1. Social Golfers
class GolfersTab:
    def __init__(self, app, f):
        self.app = app
        self.schedule = None

        ctl = ttk.LabelFrame(f, text="Parametrat", padding=PAD)
        ctl.pack(side="left", fill="y")
        self.g = tk.IntVar(value=8)
        self.p = tk.IntVar(value=4)
        self.w = tk.StringVar(value="")
        self.t = tk.DoubleVar(value=5)
        rows = [("Grupe (g)", ttk.Spinbox(ctl, from_=1, to=12, textvariable=self.g, width=6)),
                ("Lojtarë / grup (p)", ttk.Spinbox(ctl, from_=2, to=8, textvariable=self.p, width=6)),
                ("Javë (w, bosh = maks.)", ttk.Entry(ctl, textvariable=self.w, width=8)),
                ("Kufiri kohor për w (s)", ttk.Spinbox(ctl, from_=1, to=600, textvariable=self.t, width=6))]
        for i, (lbl, w) in enumerate(rows):
            ttk.Label(ctl, text=lbl).grid(row=i, column=0, sticky="w", pady=3)
            w.grid(row=i, column=1, sticky="w", pady=3)
        self.run_btn = ttk.Button(ctl, text="Ekzekuto DFS", command=self.run)
        self.run_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Separator(ctl).grid(row=6, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Label(ctl, text="Shfaq partnerët e lojtarit:").grid(row=7, column=0, columnspan=2, sticky="w")
        self.player = tk.StringVar(value="0")
        ttk.Entry(ctl, textvariable=self.player, width=6).grid(row=8, column=0, sticky="w")
        ttk.Button(ctl, text="Shfaq", command=self.partners).grid(row=8, column=1, sticky="w")

        ttk.Label(ctl, text="Shembuj:").grid(row=9, column=0, sticky="w", pady=(14, 2))
        ttk.Button(ctl, text="32 lojtarë 8×4", command=lambda: self.preset(8, 4)).grid(
            row=10, column=0, columnspan=2, sticky="ew")
        ttk.Button(ctl, text="Kirkman 15 lojtarë 5×3", command=lambda: self.preset(5, 3)).grid(
            row=11, column=0, columnspan=2, sticky="ew", pady=2)

        right = ttk.Frame(f)
        right.pack(side="left", fill="both", expand=True, padx=(PAD, 0))
        ttk.Label(right, text="Orari", font=("Helvetica", 14, "bold")).pack(anchor="w")
        tf = ttk.Frame(right)
        tf.pack(fill="both", expand=True)
        self.table = ttk.Treeview(tf, show="headings", height=12)
        sx = ttk.Scrollbar(tf, orient="horizontal", command=self.table.xview)
        self.table.configure(xscrollcommand=sx.set)
        self.table.pack(fill="both", expand=True)
        sx.pack(fill="x")
        self.status = ttk.Label(right, text="Shtyp 'Ekzekuto DFS'.", font=("Helvetica", 12))
        self.status.pack(anchor="w", pady=4)
        ttk.Label(right, text="Log-u i kërkimit", font=("Helvetica", 14, "bold")).pack(anchor="w")
        lf, self.log = text_widget(right, height=12)
        lf.pack(fill="both", expand=True)

    def preset(self, g, p):
        self.g.set(g)
        self.p.set(p)
        self.w.set("")

    def run(self):
        try:
            g, p, t = int(self.g.get()), int(self.p.get()), float(self.t.get())
            w = int(self.w.get()) if self.w.get().strip() else None
            if g < 1 or p < 2 or (w is not None and w < 1):
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Hyrja", "g ≥ 1, p ≥ 2 dhe w ≥ 1 duhet të jenë numra të plotë.")
            return
        n = g * p
        upper = (n - 1) // (p - 1)
        self.run_btn.configure(state="disabled")
        self.status.configure(text="Duke kërkuar…")
        write(self.log, f"n={n} lojtarë, g={g} grupe, p={p} lojtarë për grup\n"
                        f"Algoritmi: DFS me backtracking\n"
                        f"Kufiri i sipërm i javëve: floor((n-1)/(p-1)) = {upper}\n\n")

        def work():
            best = None
            for wk in ([w] if w else range(1, upper + 1)):
                s, found, secs = sg.solve_weeks(g, p, wk, t)
                status = sg.status_of(s, found)
                total = sg.landscape(g, p, wk)[1]
                self.app.post(write, self.log,
                              f"w={wk:<2} {status:<11} nyje={s.nodes:<9} "
                              f"backtracks={s.backtracks:<9} {secs:6.2f}s  "
                              f"|S|={sg.sci(total)}\n", True)
                if found:
                    best = (wk, [[sorted(gr) for gr in week] for week in s.schedule])
                elif not w:
                    break
            self.app.post(self.done, best, g, n)

        self.app.run_bg(work)

    def done(self, best, g, n):
        self.run_btn.configure(state="normal")
        self.table.delete(*self.table.get_children())
        if not best:
            self.schedule = None
            self.status.configure(text="Nuk u gjet orar brenda kufirit kohor.")
            return
        w, sched = best
        self.schedule = sched
        cols = ["week"] + [f"g{i}" for i in range(g)]
        self.table.configure(columns=cols)
        self.table.heading("week", text="Java")
        self.table.column("week", width=50, anchor="center", stretch=False)
        for i in range(g):
            self.table.heading(f"g{i}", text=f"Grupi {i + 1}")
            self.table.column(f"g{i}", width=105, anchor="center")
        for k, week in enumerate(sched, 1):
            groups = sorted(week)
            self.table.insert("", "end", values=[k] + [", ".join(map(str, gr)) for gr in groups])
        self.status.configure(
            text=f"Më së miri: {w} javë   objective f(S) = {sg.objective(sched)}   "
                 f"valid = {sg.is_valid(sched, n)}   "
                 f"landscape = {sg.sci(sg.landscape(g, len(sched[0][0]), w)[1])} orare")

    def partners(self):
        if not self.schedule:
            messagebox.showinfo("Partnerët", "Ekzekuto kërkimin së pari.")
            return
        try:
            x = int(self.player.get())
        except ValueError:
            return
        lines, met = [f"\nPartnerët e lojtarit {x}:\n"], []
        for k, week in enumerate(self.schedule, 1):
            for gr in week:
                if x in gr:
                    others = [v for v in gr if v != x]
                    met += others
                    lines.append(f"  java {k}: {others}\n")
        if len(lines) == 1:
            lines.append("  (ky lojtar nuk ekziston)\n")
        else:
            lines.append(f"  takoi {len(met)} lojtarë, {len(set(met))} të ndryshëm "
                         f"-> {'pa përsëritje' if len(met) == len(set(met)) else 'KA PËRSËRITJE!'}\n")
        write(self.log, "".join(lines), True)


# ==================================================================== 2. Sudoku
class SudokuTab:
    def __init__(self, app, f):
        self.app = app
        self.givens = (0,) * 81
        self.anim_job = None

        left = ttk.Frame(f)
        left.pack(side="left", fill="y")
        board = tk.Frame(left, bg="#222", padx=3, pady=3)
        board.pack()
        self.big = tkfont.Font(family="Helvetica", size=22, weight="bold")
        self.normal = tkfont.Font(family="Helvetica", size=22)
        self.cells = []
        boxes = [[tk.Frame(board, bg="#888") for _ in range(3)] for _ in range(3)]
        for br in range(3):
            for bc in range(3):
                boxes[br][bc].grid(row=br, column=bc, padx=2, pady=2)
        for r in range(9):
            row = []
            for c in range(9):
                e = tk.Entry(boxes[r // 3][c // 3], width=2, justify="center", font=self.normal,
                             bg=BG, fg=FG, relief="flat", highlightthickness=0,
                             insertbackground=FG, disabledbackground=BG)
                e.grid(row=r % 3, column=c % 3, padx=1, pady=1, ipady=6)
                row.append(e)
            self.cells.append(row)

        ctl = ttk.LabelFrame(f, text="Kontrollet", padding=PAD)
        ctl.pack(side="left", fill="both", expand=True, padx=(PAD * 2, 0))
        ttk.Label(ctl, text="Niveli").grid(row=0, column=0, sticky="w")
        self.level = tk.StringVar(value="easy")
        cb = ttk.Combobox(ctl, textvariable=self.level, values=list(sd.PUZZLES),
                          state="readonly", width=10)
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", lambda e: self.load())
        btns = ttk.Frame(ctl)
        btns.grid(row=0, column=2, sticky="w", padx=PAD)
        ttk.Button(btns, text="Reset", command=self.load).pack(side="left")
        self.animate = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctl, text="Animo zgjerimet e BFS", variable=self.animate).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Label(ctl, text="Shpejtësia (ms / hap)").grid(row=3, column=0, sticky="w")
        self.speed = tk.IntVar(value=40)
        ttk.Scale(ctl, from_=5, to=300, variable=self.speed, orient="horizontal",
                  length=180).grid(row=3, column=1, columnspan=2, sticky="w")
        self.solve_btn = ttk.Button(ctl, text="Zgjidh me BFS", command=self.solve)
        self.solve_btn.grid(row=4, column=0, columnspan=3, sticky="ew", pady=PAD)
        self.info = ttk.Label(ctl, text="", font=("Helvetica", 12), justify="left")
        self.info.grid(row=5, column=0, columnspan=3, sticky="w")
        lf, self.log = text_widget(ctl, height=14, width=60)
        lf.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=PAD)
        ctl.rowconfigure(6, weight=1)
        ctl.columnconfigure(2, weight=1)
        self.load()

    def show(self, grid, highlight=None):
        for i in range(81):
            e = self.cells[i // 9][i % 9]
            e.delete(0, "end")
            if grid[i]:
                e.insert(0, str(grid[i]))
            given = self.givens[i] != 0
            e.configure(font=self.big if given else self.normal, fg=FG if given else BLUE,
                        bg=HILITE if i == highlight else BG)

    def read(self):
        out = []
        for r in range(9):
            for c in range(9):
                t = self.cells[r][c].get().strip()
                if t in ("", "0", "."):
                    out.append(0)
                elif t.isdigit() and 1 <= int(t) <= 9:
                    out.append(int(t))
                else:
                    raise ValueError(f"Qeliza ({r + 1},{c + 1}) duhet të jetë 1..9 ose bosh")
        return tuple(out)

    def load(self):
        self.stop_anim()
        self.givens = sd.parse(sd.PUZZLES[self.level.get()])
        self.show(self.givens)
        self.describe(self.givens)

    def describe(self, grid, title=None):
        k, raw, dom = sd.landscape(grid)
        title = title or f"Sudoku {self.level.get()} ({81 - k} numra të dhënë)\n"
        write(self.log, f"{title}Qeliza bosh (variabla): {k}\nDomain: {{1..9}}\n"
                        f"Landscape: 9^{k} = {raw:.2e} mundësi\n"
                        f"Pas heqjes së vlerave të qelizave të dhëna: {dom:.2e}\n"
                        f"Objective f = konflikte + qeliza bosh = {sd.objective(grid)}\n")

    def stop_anim(self):
        if self.anim_job:
            self.app.root.after_cancel(self.anim_job)
            self.anim_job = None
        self.solve_btn.configure(state="normal")

    def solve(self):
        self.stop_anim()
        try:
            grid = self.read()
        except ValueError as e:
            messagebox.showerror("Sudoku", str(e))
            return
        if not sd.is_consistent(grid):
            messagebox.showerror("Sudoku", "Sudoku e shkel që në fillim rregullin e rreshtit/kolonës/kutisë.")
            return
        self.givens = grid
        self.show(grid)
        self.solve_btn.configure(state="disabled")
        self.info.configure(text="Duke kërkuar…")
        def work():
            # keep at most ~800 evenly spaced expansions (BFS on Hard expands millions)
            frames, stride, last = [], [1], [None]

            def record(g, d, fr):
                last[0] = (g, d, fr)
                if (st_count[0] % stride[0]) == 0:
                    frames.append(last[0])
                    if len(frames) > 800:
                        del frames[1::2]
                        stride[0] *= 2
                st_count[0] += 1

            st_count = [0]
            t0 = time.time()
            sol, st = sd.bfs_solve(grid, on_expand=record)
            if last[0] is not None and frames[-1] is not last[0]:
                frames.append(last[0])
            self.app.post(self.done, sol, st, frames, time.time() - t0)

        self.app.run_bg(work)

    def done(self, sol, st, frames, dt):
        summary = (f"BFS {'e zgjidhi' if sol else 'nuk e zgjidhi'} Sudoku-në për {dt:.3f}s\n"
                   f"  të zgjeruara={st['expanded']}  të gjeneruara={st['generated']}  "
                   f"rrugë pa dalje={st['dead_ends']}\n  frontier maks.={st['max_frontier']}  "
                   f"thellësia={st['depth']}\n")
        if sol:
            summary += f"  objective f(solution) = {sd.objective(sol)}\n"
        elif st.get("aborted"):
            summary += "  (u arrit kufiri i nyjeve)\n"
        else:
            summary += "  (nuk ka zgjidhje)\n"
        write(self.log, "\n" + summary, True)
        if not sol or not self.animate.get():
            if sol:
                self.show(sol)
            self.info.configure(text="Përfundoi." if sol else "Nuk ka zgjidhje.")
            self.solve_btn.configure(state="normal")
            return
        # replay at most ~400 evenly spaced expansions (always the last one)
        shown = frames[::max(1, len(frames) // 400)]
        if shown[-1] is not frames[-1]:
            shown.append(frames[-1])
        total = st["expanded"]
        step = max(1, total // len(shown))
        self.play(shown, 0, step, total, None)

    def play(self, frames, i, step, total, prev):
        if i >= len(frames):
            self.info.configure(text=f"Përfundoi – zgjidhja u arrit pas {total} zgjerimeve.")
            self.show(frames[-1][0])
            self.anim_job = None
            self.solve_btn.configure(state="normal")
            return
        grid, depth, frontier = frames[i]
        changed = None
        if prev is not None:
            diff = [k for k in range(81) if grid[k] != prev[k] and grid[k]]
            changed = diff[-1] if len(diff) == 1 else None
        self.show(grid, changed)
        self.info.configure(text=f"Zgjerimi {min(i * step + 1, total)} / {total}    "
                                 f"thellësia {depth}    frontier (radha) {frontier}")
        self.anim_job = self.app.root.after(int(self.speed.get()), self.play,
                                            frames, i + 1, step, total, grid)


# ============================================================= 3. Latin Square
class Cancelled(Exception):
    pass


class StoppableLatin(ls.LatinSquareIDDFS):
    """Same algorithm; it only checks a Stop flag at every node."""

    def __init__(self, n, reduced, stop):
        super().__init__(n, reduced)
        self.stop = stop

    def depth_limited(self, depth, limit):
        if self.stop.is_set():
            raise Cancelled
        return super().depth_limited(depth, limit)


class LatinTab:
    def __init__(self, app, f):
        self.app = app
        self.stop = threading.Event()

        ctl = ttk.LabelFrame(f, text="Parametrat", padding=PAD)
        ctl.pack(side="left", fill="y")
        self.n = tk.IntVar(value=5)
        self.reduced = tk.BooleanVar(value=True)
        ttk.Label(ctl, text="n").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(ctl, from_=1, to=7, textvariable=self.n, width=6).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(ctl, text="Fikso rreshtin dhe kolonën e parë\n(thyerja e simetrisë)",
                        variable=self.reduced).grid(row=4, column=0, columnspan=2, sticky="w", pady=4)
        self.run_btn = ttk.Button(ctl, text="Ekzekuto IDDFS", command=self.run)
        self.run_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 2))
        self.stop_btn = ttk.Button(ctl, text="Ndalo", command=self.stop.set, state="disabled")
        self.stop_btn.grid(row=6, column=0, columnspan=2, sticky="ew")
        ttk.Label(ctl, text="Këshillë: IDDFS është praktike deri në n = 6;\nn = 7 zgjat shumë (përdor Ndalo).",
                  foreground="#666").grid(row=7, column=0, columnspan=2, sticky="w", pady=PAD)

        mid = ttk.Frame(f)
        mid.pack(side="left", fill="y", padx=PAD)
        ttk.Label(mid, text="Iteracionet e IDDFS", font=("Helvetica", 14, "bold")).pack(anchor="w")
        self.iters = ttk.Treeview(mid, columns=("limit", "nodes", "result"), show="headings", height=22)
        for col, w, title in (("limit", 80, "Kufiri"), ("nodes", 110, "Nyje"), ("result", 80, "Rezultati")):
            self.iters.heading(col, text=title)
            self.iters.column(col, width=w, anchor="center")
        sy = ttk.Scrollbar(mid, orient="vertical", command=self.iters.yview)
        self.iters.configure(yscrollcommand=sy.set)
        self.iters.pack(side="left", fill="y", expand=True)
        sy.pack(side="left", fill="y")

        right = ttk.Frame(f)
        right.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(right, bg=BG, width=480, height=480, highlightthickness=0)
        self.canvas.pack(anchor="nw")
        self.info = ttk.Label(right, text="", font=("Helvetica", 12), justify="left")
        self.info.pack(anchor="w", pady=PAD)

    def draw(self, grid, given_mask=None):
        c = self.canvas
        c.delete("all")
        n = len(grid)
        size = min(60, 460 // max(n, 1))
        fnt = ("Helvetica", max(9, size // 2), "bold")
        for r in range(n):
            for k in range(n):
                v = grid[r][k]
                if v:
                    rr, gg, bb = colorsys.hsv_to_rgb((v - 1) / n, 0.35, 1.0)
                    fill = f"#{int(rr * 255):02x}{int(gg * 255):02x}{int(bb * 255):02x}"
                else:
                    fill = BG
                x0, y0 = 10 + k * size, 10 + r * size
                c.create_rectangle(x0, y0, x0 + size, y0 + size, fill=fill, outline="#555")
                if v:
                    bold = given_mask and given_mask[r][k]
                    c.create_text(x0 + size / 2, y0 + size / 2, text=str(v), fill=FG,
                                  font=fnt if bold else ("Helvetica", max(9, size // 2)))

    def run(self):
        try:
            n = int(self.n.get())
            if not 1 <= n <= 7:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Hyrja", "n duhet të jetë numër i plotë nga 1 deri në 7.")
            return
        reduced = self.reduced.get()
        self.stop.clear()
        self.iters.delete(*self.iters.get_children())
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        raw, perm = ls.landscape(n)
        known = f"\nKatrorë latinë të rendit {n}: {ls.sci(ls.KNOWN[n])}" if n in ls.KNOWN else ""
        self.landscape_txt = (f"Landscape: n^(n²) = {ls.sci(raw)} tabela, "
                              f"(n!)^n = {ls.sci(perm)}{known}")
        self.info.configure(text="Duke kërkuar…\n" + self.landscape_txt)
        self.canvas.delete("all")

        def work():
            s = StoppableLatin(n, reduced, self.stop)
            given = [[bool(v) for v in row] for row in s.grid]
            t0 = time.time()
            try:
                found = s.iddfs(verbose=False,
                                on_iteration=lambda L, nd, res: self.app.post(
                                    self.add_iter, L, nd, res))
                self.app.post(self.done, s, given, found, time.time() - t0, False)
            except Cancelled:
                self.app.post(self.done, s, given, False, time.time() - t0, True)

        self.app.run_bg(work)

    def add_iter(self, limit, nodes, res):
        item = self.iters.insert("", "end", values=(limit, f"{nodes:,}", res))
        self.iters.see(item)

    def done(self, s, given, found, dt, stopped):
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if stopped:
            self.info.configure(text=f"U ndal pas {dt:.1f}s, {s.nodes:,} nyje.\n"
                                     + self.landscape_txt)
            return
        if not found:
            self.info.configure(text="Nuk u gjet katror latin.\n" + self.landscape_txt)
            return
        self.draw(s.grid, given)
        self.info.configure(
            text=f"U gjet për {dt:.3f}s   nyje të vizituara = {s.nodes:,}   "
                 f"iteracione = {len(s.iter_nodes)}\n"
                 f"Variabla = {s.goal_depth} qeliza (bold = të fiksuara), objective f = {ls.objective(s.grid)}\n"
                 + self.landscape_txt)


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("aqua" if sys.platform == "darwin" else "clam")
    except tk.TclError:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
