"""
Social Golfers Problem - DFS with backtracking.

n = g * p golfers play every week in g groups of p players.
Goal: a schedule for w weeks where no two golfers meet twice.

Variable: x[week][group][slot]   Domain: {0, ..., n-1}
C1: every player plays once per week
C2: two players share a group at most once

Run:  python social_golfers.py [-g 8] [-p 4] [-w weeks] [-t seconds]
"""

import argparse
import math
import sys
import time


class SocialGolfersDFS:
    def __init__(self, g, p, w, time_limit=None):
        self.g, self.p, self.w = g, p, w
        self.n = g * p
        self.deadline = time.time() + time_limit if time_limit else None
        # schedule[week][group] = players in that group
        self.schedule = [[[] for _ in range(g)] for _ in range(w)]
        # met[i][j] = True if i and j already played together
        self.met = [[False] * self.n for _ in range(self.n)]
        # used[week][i] = True if player i is already placed that week
        self.used = [[False] * self.n for _ in range(w)]
        self.nodes = 0
        self.backtracks = 0
        self.aborted = False

    # ---- place / remove a player
    def _place(self, week, group, player):
        members = self.schedule[week][group]
        for m in members:
            self.met[m][player] = self.met[player][m] = True
        members.append(player)
        self.used[week][player] = True

    def _remove(self, week, group):
        members = self.schedule[week][group]
        player = members.pop()
        for m in members:
            self.met[m][player] = self.met[player][m] = False
        self.used[week][player] = False

    def _candidates(self, week, group, slot):
        """Players that can go in this slot without breaking C1 or C2."""
        used = self.used[week]
        if slot == 0:
            # symmetry breaking: the group starts with the smallest free player
            for v in range(self.n):
                if not used[v]:
                    return [v]
            return []
        members = self.schedule[week][group]
        return [v for v in range(members[-1] + 1, self.n)        # increasing order (symmetry)
                if not used[v]                                     # C1
                and not any(self.met[m][v] for m in members)]      # C2

    # ---- DFS
    def _dfs(self, pos):
        """pos = number of the next free slot (week by week, group by group)."""
        self.nodes += 1
        if self.deadline and self.nodes % 10_000 == 0 and time.time() > self.deadline:
            self.aborted = True
        if self.aborted:
            return False

        # which slot is next (fixed order -> uninformed search)
        week, rest = divmod(pos, self.g * self.p)
        group, slot = divmod(rest, self.p)
        if week == self.w:                           # goal test
            return True

        for v in self._candidates(week, group, slot):    # try values 0, 1, 2, ...
            self._place(week, group, v)
            if self._dfs(pos + 1):                       # go deeper
                return True
            self._remove(week, group)                    # BACKTRACK
            if self.aborted:
                return False
        self.backtracks += 1
        return False

    def solve(self):
        sys.setrecursionlimit(10_000)
        return self._dfs(0)


# ---- objective function
def objective(schedule):
    """f(S) = number of repeated meetings. Goal: f(S) = 0."""
    meet = {}
    for wk in schedule:
        for grp in wk:
            for i in range(len(grp)):
                for j in range(i + 1, len(grp)):
                    key = (min(grp[i], grp[j]), max(grp[i], grp[j]))
                    meet[key] = meet.get(key, 0) + 1
    return sum(c - 1 for c in meet.values() if c > 1)


def is_valid(schedule, n):
    return all(sorted(x for grp in wk for x in grp) == list(range(n)) for wk in schedule) \
        and objective(schedule) == 0


# ---- landscape
def landscape(g, p, w):
    """raw    = |D|^(variables)       = n^(n*w)
    groups = real different schedules = (n! / ((p!)^g * g!))^w"""
    n = g * p
    raw = n ** (n * w)
    groups = (math.factorial(n) // (math.factorial(p) ** g * math.factorial(g))) ** w
    return raw, groups


def sci(x):
    return f"{x:.2e}" if x >= 10 ** 6 else str(x)


def print_schedule(schedule, g):
    head = "Week | " + " | ".join(f"Group {i + 1:<5}" for i in range(g))
    print(head)
    print("-" * len(head))
    for k, wk in enumerate(schedule, 1):
        print(f"{k:<4} | " + " | ".join(f"{','.join(map(str, grp)):<11}" for grp in wk))


def solve_weeks(g, p, w, time_limit):
    t0 = time.time()
    s = SocialGolfersDFS(g, p, w, time_limit=time_limit)
    found = s.solve()
    return s, found, time.time() - t0


def status_of(solver, found):
    if found:
        return "FOUND"
    return "TIMEOUT" if solver.aborted else "NO SOLUTION"   # whole tree explored


def main():
    ap = argparse.ArgumentParser(description="Social Golfers – DFS with backtracking")
    ap.add_argument("-g", type=int, default=8, help="number of groups")
    ap.add_argument("-p", type=int, default=4, help="players per group")
    ap.add_argument("-w", type=int, default=None, help="weeks (omit = find maximum)")
    ap.add_argument("-t", type=float, default=30.0, help="time limit per w (seconds)")
    a = ap.parse_args()

    g, p = a.g, a.p
    n = g * p
    upper = (n - 1) // (p - 1)
    print(f"Social Golfers: n={n} golfers, g={g} groups, p={p} golfers/group")
    print(f"Upper bound on weeks: floor((n-1)/(p-1)) = {upper}\n")

    weeks = [a.w] if a.w else range(1, upper + 1)
    best = None
    for w in weeks:
        total = landscape(g, p, w)[1]
        s, found, secs = solve_weeks(g, p, w, a.t)
        print(f"w={w:<2} {status_of(s, found):<11} nodes={s.nodes:<10} "
              f"backtracks={s.backtracks:<10} time={secs:6.2f}s   landscape |S| = {sci(total)}")
        if found:
            best = (w, [[list(gr) for gr in wk] for wk in s.schedule])
        elif not a.w:
            break

    if best:
        w, sched = best
        print(f"\nBest schedule: {w} weeks, objective f(S) = {objective(sched)}, "
              f"valid = {is_valid(sched, n)}\n")
        print_schedule(sched, g)
        raw, groups = landscape(g, p, w)
        print(f"\nLandscape for w={w}:")
        print(f"  |D|^(variables)  = n^(n*w)              = {sci(raw)}")
        print(f"  real schedules   = (n!/((p!)^g * g!))^w = {sci(groups)}")


if __name__ == "__main__":
    main()
