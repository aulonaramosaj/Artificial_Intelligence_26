"""
Latin Square - IDDFS with backtracking.

n x n grid with the numbers 1..n, every number once in every row and column.

Variable: X[r][c] for every cell   Domain: {1, ..., n}
Constraints: all different in every row and every column

Run:  python latin_square_iddfs.py [n] [--full] [-q]
"""

import argparse
import math
import sys
import time


class LatinSquareIDDFS:
    def __init__(self, n, reduced=True):
        self.n = n
        self.grid = [[0] * n for _ in range(n)]
        # bitmasks of the values already used in each row / column
        self.row_used = [0] * n
        self.col_used = [0] * n
        # symmetry breaking: first row and first column fixed to 1..n
        if reduced:
            for k in range(n):
                self._assign(0, k, k + 1)
                if k:
                    self._assign(k, 0, k + 1)
        # variables = empty cells, filled row by row (depth = filled cells)
        self.cells = [(r, c) for r in range(n) for c in range(n) if not self.grid[r][c]]
        self.goal_depth = len(self.cells)
        self.nodes = 0                # nodes over all iterations
        self.iter_nodes = []          # (limit, nodes) for every iteration
        self.backtracks = 0

    # ---- place / remove a value
    def _legal(self, r, c):
        """Values not yet used in row r or column c."""
        used = self.row_used[r] | self.col_used[c]
        return [v for v in range(1, self.n + 1) if not used >> v & 1]

    def _assign(self, r, c, v):
        self.grid[r][c] = v
        self.row_used[r] |= 1 << v
        self.col_used[c] |= 1 << v

    def _unassign(self, r, c):
        v = self.grid[r][c]
        self.grid[r][c] = 0
        self.row_used[r] &= ~(1 << v)
        self.col_used[c] &= ~(1 << v)

    # ---- depth-limited DFS
    def depth_limited(self, depth, limit):
        """Returns 'found', 'cutoff' (limit reached) or 'failure' (no solution)."""
        self.nodes += 1
        self._count += 1
        if depth == self.goal_depth:          # goal test: all cells filled
            return "found"
        if depth == limit:                    # depth limit reached
            return "cutoff"
        r, c = self.cells[depth]              # next cell (fixed order)
        cutoff = False
        for v in self._legal(r, c):           # try values 1, 2, ..., n
            self._assign(r, c, v)
            res = self.depth_limited(depth + 1, limit)   # go deeper
            if res == "found":
                return "found"
            if res == "cutoff":
                cutoff = True
            self._unassign(r, c)              # BACKTRACK
        if not cutoff:
            self.backtracks += 1
        return "cutoff" if cutoff else "failure"

    # ---- IDDFS
    def iddfs(self, verbose=True, on_iteration=None):
        """Depth-limited DFS with limit 0, 1, 2, ... until a solution is found.
        on_iteration is used only by the GUI."""
        sys.setrecursionlimit(10_000)
        limit = 0
        while True:
            self._count = 0
            res = self.depth_limited(0, limit)
            self.iter_nodes.append((limit, self._count))
            if verbose:
                print(f"  iteration limit={limit:<4} nodes={self._count:<10} -> {res}")
            if on_iteration:
                on_iteration(limit, self._count, res)
            if res == "found":
                return True
            if res == "failure":              # whole tree explored
                return False
            limit += 1


# ---- objective function
def objective(grid):
    """f = sum over rows and columns of (n - distinct values). Goal: f = 0."""
    n = len(grid)
    rows = sum(n - len(set(row)) for row in grid)
    cols = sum(n - len({grid[r][c] for r in range(n)}) for c in range(n))
    return rows + cols


# ---- landscape
def landscape(n):
    """raw = n^(n^2) (any value in any cell), rows_perm = (n!)^n (every row a permutation)."""
    raw = n ** (n * n)
    rows_perm = math.factorial(n) ** n
    return raw, rows_perm


def sci(x):
    return f"{x:.2e}" if x >= 10 ** 6 else str(x)


# number of Latin squares of order n (OEIS A002860)
KNOWN = {1: 1, 2: 2, 3: 12, 4: 576, 5: 161280, 6: 812851200,
         7: 61479419904000, 8: 108776032459082956800}


def main():
    ap = argparse.ArgumentParser(description="Latin square – IDDFS with backtracking")
    ap.add_argument("n", type=int, nargs="?", default=5)
    ap.add_argument("--full", action="store_true", help="no symmetry breaking")
    ap.add_argument("-q", "--quiet", action="store_true", help="do not print iterations")
    a = ap.parse_args()
    n = a.n
    if n < 1:
        ap.error("n must be at least 1")

    raw, perm = landscape(n)
    print(f"Landscape: n^(n^2) = {sci(raw)} raw grids, (n!)^n = {sci(perm)} grids "
          f"with permutation rows" + (f", {sci(KNOWN[n])} Latin squares" if n in KNOWN else ""))

    s = LatinSquareIDDFS(n, reduced=not a.full)
    print(f"Variables: {s.goal_depth} empty cells "
          f"({'all cells' if a.full else 'first row and column fixed to 1..n'}), "
          f"domain {{1..{n}}}, goal depth = {s.goal_depth}")
    t0 = time.time()
    print("Mode: IDDFS with backtracking")
    found = s.iddfs(verbose=not a.quiet)
    dt = time.time() - t0

    if not found:
        print("No Latin square found.")
        return
    print(f"\nFound in {dt:.3f}s, nodes visited = {s.nodes}, "
          f"iterations = {len(s.iter_nodes)}, objective f = {objective(s.grid)}\n")
    width = len(str(n))
    for row in s.grid:
        print(" ".join(f"{v:>{width}}" for v in row))


if __name__ == "__main__":
    main()
