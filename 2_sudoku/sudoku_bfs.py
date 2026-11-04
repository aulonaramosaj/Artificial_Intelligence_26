"""
Sudoku Solver - BFS with backtracking.

Variable: X[r][c] for every empty cell   Domain: {1, ..., 9}
Constraints: all different in every row, column and 3x3 box

Run:  python sudoku_bfs.py [easy|medium|hard]   or   --grid "<81 chars>"
"""

import argparse
import math
import time
from collections import deque

# '.' = empty cell
PUZZLES = {
    "easy": (
        "....2.5.."
        "..356.1.4"
        "......2.9"
        "8.2...63."
        "36...5941"
        "91.3.6852"
        "27.6134.8"
        "..9..83.6"
        "...49.7.."
    ),
    "medium": (
        "..9.31..."
        "...5.7..1"
        ".714....9"
        "7..3..1.."
        ".3..1..5."
        "1.5.8..97"
        "....432.6"
        ".4...5..."
        ".1.26..45"
    ),
    "hard": (                       # World's hardest Sudoku
        "8........"
        "..36....."
        ".7..9.2.."
        ".5...7..."
        "....457.."
        "...1...3."
        "..1....68"
        "..85...1."
        ".9....4.."
    ),
}


def parse(text):
    """81-character string -> tuple of 81 numbers (0 = empty)."""
    text = [ch for ch in text if ch in "0123456789."]
    if len(text) != 81:
        raise ValueError("A Sudoku needs exactly 81 cells")
    return tuple(0 if ch in ".0" else int(ch) for ch in text)


def peers_of(i):
    """Cells in the same row, column or box as cell i."""
    r, c = divmod(i, 9)
    br, bc = 3 * (r // 3), 3 * (c // 3)
    ps = {r * 9 + k for k in range(9)} | {k * 9 + c for k in range(9)}
    ps |= {(br + a) * 9 + bc + b for a in range(3) for b in range(3)}
    ps.discard(i)
    return tuple(ps)


PEERS = [peers_of(i) for i in range(81)]


def legal_values(grid, i):
    """Values 1..9 that no peer of cell i uses yet."""
    used = {grid[j] for j in PEERS[i]}
    return [v for v in range(1, 10) if v not in used]


def objective(grid):
    """f = conflicts + empty cells. Goal: f = 0."""
    conflicts = sum(1 for i in range(81) if grid[i]
                    for j in PEERS[i] if j > i and grid[j] == grid[i])
    return conflicts + grid.count(0)


def is_consistent(grid):
    """True if no row, column or box has the same number twice."""
    return all(grid[i] == 0 or all(grid[j] != grid[i] for j in PEERS[i]) for i in range(81))


def next_cell(grid):
    """First empty cell (row by row) and its legal values, None if full.
    Fixed order -> uninformed search."""
    for i in range(81):
        if grid[i] == 0:
            return i, legal_values(grid, i)
    return None


def bfs_solve(start, max_nodes=5_000_000, on_expand=None):
    """Returns (solution, statistics). on_expand is used only by the GUI."""
    stats = {"expanded": 0, "generated": 1, "dead_ends": 0, "max_frontier": 1,
             "depth": 0}
    if not is_consistent(start):
        return None, stats
    queue = deque([(start, 0)])
    while queue:
        grid, depth = queue.popleft()               # 1. take the oldest state (FIFO)
        stats["expanded"] += 1
        stats["depth"] = max(stats["depth"], depth)
        if on_expand:
            on_expand(grid, depth, len(queue))
        choice = next_cell(grid)
        if choice is None:                          # 2. goal test: no empty cells
            return grid, stats
        cell, values = choice
        if not values:                              # 3. dead end -> drop it (backtrack)
            stats["dead_ends"] += 1
            continue
        for v in values:                            # 4. add children to the queue
            child = list(grid)
            child[cell] = v
            queue.append((tuple(child), depth + 1))
            stats["generated"] += 1
        stats["max_frontier"] = max(stats["max_frontier"], len(queue))
        if stats["generated"] > max_nodes:
            stats["aborted"] = True
            return None, stats
    return None, stats


def landscape(grid):
    """raw = 9^(empty cells), domains = product of the legal values of each empty cell."""
    empties = grid.count(0)
    raw = 9 ** empties
    domains = math.prod(len(legal_values(grid, i)) for i in range(81) if grid[i] == 0)
    return empties, raw, domains


def show(grid):
    lines = []
    for r in range(9):
        if r % 3 == 0 and r:
            lines.append("------+-------+------")
        row = ""
        for c in range(9):
            if c % 3 == 0 and c:
                row += "| "
            v = grid[r * 9 + c]
            row += (str(v) if v else ".") + " "
        lines.append(row.rstrip())
    return "\n".join(lines)


def solve_and_report(name, grid):
    empties, raw, dom = landscape(grid)
    print(f"=== {name.upper()} ===  empty cells: {empties}")
    print(show(grid))
    print(f"Landscape: 9^{empties} = {raw:.2e} raw assignments; "
          f"after removing values used by given cells: {dom:.2e}")
    t0 = time.time()
    sol, st = bfs_solve(grid)
    dt = time.time() - t0
    if sol:
        print(f"\nSolved by BFS in {dt:.3f}s  (expanded={st['expanded']}, "
              f"generated={st['generated']}, dead ends={st['dead_ends']}, "
              f"max frontier={st['max_frontier']}, depth={st['depth']})")
        print(f"Objective f(solution) = {objective(sol)}\n")
        print(show(sol))
    else:
        reason = "node limit reached" if st.get("aborted") else "no solution exists"
        print(f"\nNot solved ({reason}) after {dt:.2f}s, generated={st['generated']}")
    print()


def main():
    ap = argparse.ArgumentParser(description="Sudoku – BFS with backtracking")
    ap.add_argument("level", nargs="*", help="easy / medium / hard (default: all)")
    ap.add_argument("--grid", help="your own puzzle, 81 chars, '.' or 0 = empty")
    a = ap.parse_args()

    if a.grid:
        solve_and_report("custom", parse(a.grid))
    else:
        for lvl in a.level or list(PUZZLES):
            if lvl not in PUZZLES:
                ap.error(f"unknown level '{lvl}', choose from {', '.join(PUZZLES)}")
            solve_and_report(lvl, parse(PUZZLES[lvl]))


if __name__ == "__main__":
    main()
