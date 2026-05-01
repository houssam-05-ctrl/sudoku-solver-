"""
Sudoku Solver — AC-3 Constraint Propagation + Heuristic Backtracking Search
============================================================================

This module models Sudoku as a Constraint Satisfaction Problem (CSP) and solves
it by combining:

  1. AC-3 (Arc Consistency #3) — for domain reduction via constraint propagation.
  2. Backtracking Search — depth-first exploration of the assignment space.
  3. MRV (Minimum Remaining Values) — choose the variable with fewest legal values.
  4. Degree Heuristic — break MRV ties by choosing the most-constrained variable.
  5. LCV (Least Constraining Value) — order values to maximise future flexibility.

Author : Houssam El Bakkouri
"""

from __future__ import annotations

import copy
import time
from collections import deque
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# 1.  CSP DATA STRUCTURES
# ──────────────────────────────────────────────────────────────────────────────

class SudokuCSP:
    """
    Models a 9×9 Sudoku puzzle as a binary CSP.

    Variables : 81 cells, each identified by (row, col) where row, col ∈ {0..8}.
    Domains   : Each variable's domain is a set of integers {1..9}.
                Pre-filled cells have a singleton domain.
    Constraints: All-different constraints along every row, column, and 3×3 box.
                 Decomposed into 810 binary arcs (Xi ≠ Xj for every constrained pair).
    """

    def __init__(self, grid: list[list[int]]) -> None:
        """
        Initialise the CSP from a 9×9 grid.

        Parameters
        ----------
        grid : list[list[int]]
            9×9 list-of-lists. 0 denotes an empty cell.
        """
        # --- Variables: every cell on the board ---
        self.variables: list[tuple[int, int]] = [
            (r, c) for r in range(9) for c in range(9)
        ]

        # --- Domains: set of possible values per variable ---
        self.domains: dict[tuple[int, int], set[int]] = {}
        for r in range(9):
            for c in range(9):
                if grid[r][c] != 0:
                    # Given clue → singleton domain
                    self.domains[(r, c)] = {grid[r][c]}
                else:
                    # Unknown → full domain
                    self.domains[(r, c)] = set(range(1, 10))

        # --- Neighbours: precompute the set of peers for each cell ---
        # Two cells are neighbours iff they share a row, column, or 3×3 box.
        self.neighbours: dict[tuple[int, int], set[tuple[int, int]]] = {
            v: set() for v in self.variables
        }
        for v in self.variables:
            self.neighbours[v] = self._compute_neighbours(v)

        # --- Arcs: all directed constraint arcs (Xi, Xj) ---
        self.arcs: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for v in self.variables:
            for n in self.neighbours[v]:
                self.arcs.append((v, n))

    @staticmethod
    def _compute_neighbours(cell: tuple[int, int]) -> set[tuple[int, int]]:
        """Return all cells that share a row, column, or box with `cell`."""
        r, c = cell
        neighbours: set[tuple[int, int]] = set()

        # Same row
        for cc in range(9):
            if cc != c:
                neighbours.add((r, cc))

        # Same column
        for rr in range(9):
            if rr != r:
                neighbours.add((rr, c))

        # Same 3×3 box
        box_r, box_c = 3 * (r // 3), 3 * (c // 3)
        for rr in range(box_r, box_r + 3):
            for cc in range(box_c, box_c + 3):
                if (rr, cc) != (r, c):
                    neighbours.add((rr, cc))

        return neighbours


# ──────────────────────────────────────────────────────────────────────────────
# 2.  AC-3  (Arc Consistency Algorithm #3)
# ──────────────────────────────────────────────────────────────────────────────

def ac3(
    csp: SudokuCSP,
    arcs: Optional[list[tuple[tuple[int, int], tuple[int, int]]]] = None,
    log: bool = False,
) -> bool:
    """
    Enforce arc consistency across the CSP.

    Algorithm
    ---------
    1. Initialise a queue with all arcs (or a subset if provided).
    2. Dequeue an arc (Xi, Xj).
    3. Call REVISE(Xi, Xj) — remove any value from Di that has *no* consistent
       partner in Dj.
    4. If Di was revised:
       a. If Di is empty → failure (no valid assignment exists).
       b. Else, enqueue all arcs (Xk, Xi) for every neighbour Xk ≠ Xj.
    5. Repeat until the queue is empty.

    Returns
    -------
    bool
        True if the CSP is still solvable (no empty domain), False otherwise.
    """
    # Use a deque for O(1) pops from the front
    queue: deque[tuple[tuple[int, int], tuple[int, int]]] = deque(
        arcs if arcs is not None else csp.arcs
    )

    revisions = 0  # Counter for demonstration

    while queue:
        xi, xj = queue.popleft()
        if _revise(csp, xi, xj):
            revisions += 1
            if log:
                print(f"  AC-3: revised {xi}, domain now {sorted(csp.domains[xi])}")

            # Domain wiped out → inconsistency
            if len(csp.domains[xi]) == 0:
                if log:
                    print(f"  AC-3: domain of {xi} is EMPTY → failure")
                return False

            # Propagate: re-check all arcs pointing into Xi
            for xk in csp.neighbours[xi]:
                if xk != xj:
                    queue.append((xk, xi))

    if log and revisions > 0:
        print(f"  AC-3 complete: {revisions} revision(s) applied.")
    return True


def _revise(csp: SudokuCSP, xi: tuple[int, int], xj: tuple[int, int]) -> bool:
    """
    Remove values from the domain of Xi that are inconsistent with Xj.

    A value `v` in Di is inconsistent if there is *no* value `w` in Dj such
    that v ≠ w  (i.e., the Sudoku all-different constraint is satisfiable).

    In practice, v is inconsistent only when Dj == {v} — meaning Xj is forced
    to take the same value, which would violate the constraint.

    Returns True if any value was removed from Di.
    """
    revised = False
    to_remove: list[int] = []

    for v in csp.domains[xi]:
        # Is there at least one value in Dj that satisfies Xi ≠ Xj?
        # That's any value w in Dj where w ≠ v.
        if not any(w != v for w in csp.domains[xj]):
            to_remove.append(v)

    for v in to_remove:
        csp.domains[xi].discard(v)
        revised = True

    return revised


# ──────────────────────────────────────────────────────────────────────────────
# 3.  HEURISTIC FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def select_unassigned_variable(csp: SudokuCSP) -> tuple[int, int]:
    """
    Choose the next variable to assign using:

      1. MRV (Minimum Remaining Values) — pick the variable whose domain is
         smallest (but > 1, since size 1 means already determined).
         Rationale: a smaller domain means fewer choices to explore, so
         failures are detected earlier (fail-first principle).

      2. Degree Heuristic (tie-breaker) — among MRV-tied variables, pick the
         one involved in the most constraints with *unassigned* neighbours.
         Rationale: constraining more peers propagates information faster.

    Returns
    -------
    tuple[int, int]
        The (row, col) of the chosen variable.
    """
    # Candidates: unassigned variables (domain size > 1)
    unassigned = [v for v in csp.variables if len(csp.domains[v]) > 1]

    if not unassigned:
        # All assigned — shouldn't normally reach here during search
        raise ValueError("No unassigned variables remain.")

    # --- MRV: sort by domain size ascending ---
    min_domain_size = min(len(csp.domains[v]) for v in unassigned)
    mrv_candidates = [v for v in unassigned if len(csp.domains[v]) == min_domain_size]

    if len(mrv_candidates) == 1:
        return mrv_candidates[0]

    # --- Degree Heuristic: among MRV ties, pick highest degree ---
    # Degree = number of unassigned neighbours
    def degree(v: tuple[int, int]) -> int:
        return sum(1 for n in csp.neighbours[v] if len(csp.domains[n]) > 1)

    return max(mrv_candidates, key=degree)


def order_domain_values(
    csp: SudokuCSP, var: tuple[int, int]
) -> list[int]:
    """
    Order the domain values of `var` using the Least Constraining Value (LCV)
    heuristic.

    For each candidate value `v`, count how many values it would eliminate
    from the domains of unassigned neighbours.  Return values sorted in
    *ascending* order of eliminations — the value that rules out the fewest
    choices for peers comes first.

    Rationale: LCV maximises the remaining flexibility for other variables,
    making it more likely that we find a solution without backtracking.
    """
    def count_conflicts(value: int) -> int:
        """Count how many peer domain values would be eliminated by choosing `value`."""
        conflicts = 0
        for neighbour in csp.neighbours[var]:
            if len(csp.domains[neighbour]) > 1 and value in csp.domains[neighbour]:
                conflicts += 1
        return conflicts

    return sorted(csp.domains[var], key=count_conflicts)


# ──────────────────────────────────────────────────────────────────────────────
# 4.  BACKTRACKING SEARCH WITH AC-3 INFERENCE
# ──────────────────────────────────────────────────────────────────────────────

class SolverStats:
    """Accumulates statistics during the search for analysis."""

    def __init__(self) -> None:
        self.backtracks: int = 0
        self.assignments: int = 0
        self.ac3_calls: int = 0
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    @property
    def elapsed(self) -> float:
        return self.end_time - self.start_time


def backtracking_search(
    csp: SudokuCSP, stats: SolverStats, log: bool = False
) -> bool:
    """
    Solve the CSP using recursive backtracking with AC-3 inference.

    Algorithm
    ---------
    1. If every variable has a singleton domain → solution found.
    2. Select an unassigned variable using MRV + Degree Heuristic.
    3. For each value in the domain (ordered by LCV):
       a. Create a deep copy of the domains (for backtracking).
       b. Assign the value (set domain to singleton).
       c. Run AC-3 restricted to arcs affected by this assignment.
       d. If AC-3 succeeds and recursive call succeeds → return True.
       e. Else, restore domains (backtrack).
    4. If no value works → return False (trigger backtracking in caller).

    Returns
    -------
    bool
        True if a consistent complete assignment was found.
    """
    # --- Base case: all domains are singletons → solved ---
    if all(len(csp.domains[v]) == 1 for v in csp.variables):
        return True

    # --- Select variable (MRV + Degree) ---
    var = select_unassigned_variable(csp)
    if log:
        print(f"\nSelected variable {var} (domain: {sorted(csp.domains[var])})")

    # --- Try each value (LCV order) ---
    for value in order_domain_values(csp, var):
        stats.assignments += 1

        if log:
            print(f"  Trying {var} = {value}")

        # Save domains for backtracking
        saved_domains = {v: set(d) for v, d in csp.domains.items()}

        # Assign: set domain to singleton
        csp.domains[var] = {value}

        # --- Inference: run AC-3 on arcs affected by this assignment ---
        # Only enqueue arcs (Xk, var) for each neighbour Xk
        inference_arcs = [(xk, var) for xk in csp.neighbours[var]]
        stats.ac3_calls += 1

        if ac3(csp, arcs=inference_arcs, log=log):
            # AC-3 succeeded — recurse
            if backtracking_search(csp, stats, log=log):
                return True

        # --- Backtrack: restore all domains ---
        if log:
            print(f"  Backtracking from {var} = {value}")
        stats.backtracks += 1
        csp.domains = saved_domains

    return False


# ──────────────────────────────────────────────────────────────────────────────
# 5.  SOLVER ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def solve(grid: list[list[int]], log: bool = False) -> tuple[
    Optional[list[list[int]]], SolverStats
]:
    """
    Solve a 9×9 Sudoku puzzle.

    Parameters
    ----------
    grid : list[list[int]]
        The puzzle. 0 = empty cell.
    log : bool
        If True, print intermediate AC-3 and search steps.

    Returns
    -------
    solution : list[list[int]] or None
        The completed grid, or None if unsolvable.
    stats : SolverStats
        Performance statistics.
    """
    stats = SolverStats()
    stats.start_time = time.perf_counter()

    # Build the CSP model
    csp = SudokuCSP(grid)

    if log:
        print("=" * 60)
        print("PHASE 1: AC-3 Preprocessing")
        print("=" * 60)

    # --- Phase 1: AC-3 Preprocessing ---
    # Run AC-3 on ALL arcs to reduce domains before search begins.
    stats.ac3_calls += 1
    if not ac3(csp, log=log):
        stats.end_time = time.perf_counter()
        return None, stats  # Inconsistent puzzle

    if log:
        _print_domains(csp)
        print()
        print("=" * 60)
        print("PHASE 2: Backtracking Search (MRV + Degree + LCV + AC-3)")
        print("=" * 60)

    # Check if AC-3 alone solved it
    if all(len(csp.domains[v]) == 1 for v in csp.variables):
        if log:
            print("AC-3 alone solved the puzzle — no search needed!")
        solution = _domains_to_grid(csp)
        stats.end_time = time.perf_counter()
        return solution, stats

    # --- Phase 2: Backtracking Search ---
    if backtracking_search(csp, stats, log=log):
        solution = _domains_to_grid(csp)
        stats.end_time = time.perf_counter()
        return solution, stats
    else:
        stats.end_time = time.perf_counter()
        return None, stats


# ──────────────────────────────────────────────────────────────────────────────
# 6.  UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def _domains_to_grid(csp: SudokuCSP) -> list[list[int]]:
    """Convert singleton domains back to a 9×9 integer grid."""
    grid = [[0] * 9 for _ in range(9)]
    for (r, c), domain in csp.domains.items():
        grid[r][c] = next(iter(domain))
    return grid


def _print_domains(csp: SudokuCSP) -> None:
    """Pretty-print domain sizes after AC-3 preprocessing."""
    print("\nDomain sizes after AC-3 preprocessing:")
    for r in range(9):
        row_info = []
        for c in range(9):
            d = csp.domains[(r, c)]
            if len(d) == 1:
                row_info.append(f" {next(iter(d))} ")
            else:
                row_info.append(f"({len(d)})")
        if r % 3 == 0 and r != 0:
            print("  ------+-------+------")
        line = " ".join(row_info[:3]) + " | " + " ".join(row_info[3:6]) + " | " + " ".join(row_info[6:])
        print(f"  {line}")


def print_grid(grid: list[list[int]], title: str = "") -> None:
    """Pretty-print a 9×9 Sudoku grid."""
    if title:
        print(f"\n{title}")
        print("  " + "-" * 25)
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("  ------+-------+------")
        row_str = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str += "| "
            val = grid[r][c]
            row_str += (str(val) if val != 0 else ".") + " "
        print(f"  {row_str.rstrip()}")
    print()


def validate_solution(grid: list[list[int]]) -> bool:
    """
    Verify that a completed grid satisfies all Sudoku constraints:
      - Every row contains {1..9}
      - Every column contains {1..9}
      - Every 3×3 box contains {1..9}
    """
    target = set(range(1, 10))

    # Check rows
    for r in range(9):
        if set(grid[r]) != target:
            return False

    # Check columns
    for c in range(9):
        if {grid[r][c] for r in range(9)} != target:
            return False

    # Check 3×3 boxes
    for box_r in range(0, 9, 3):
        for box_c in range(0, 9, 3):
            vals = {
                grid[r][c]
                for r in range(box_r, box_r + 3)
                for c in range(box_c, box_c + 3)
            }
            if vals != target:
                return False

    return True


# ──────────────────────────────────────────────────────────────────────────────
# 7.  DEMONSTRATION
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Run the solver on example puzzles and display results."""

    # ── Example 1: Medium-difficulty puzzle ──
    puzzle_medium = [
        [5, 3, 0,  0, 7, 0,  0, 0, 0],
        [6, 0, 0,  1, 9, 5,  0, 0, 0],
        [0, 9, 8,  0, 0, 0,  0, 6, 0],

        [8, 0, 0,  0, 6, 0,  0, 0, 3],
        [4, 0, 0,  8, 0, 3,  0, 0, 1],
        [7, 0, 0,  0, 2, 0,  0, 0, 6],

        [0, 6, 0,  0, 0, 0,  2, 8, 0],
        [0, 0, 0,  4, 1, 9,  0, 0, 5],
        [0, 0, 0,  0, 8, 0,  0, 7, 9],
    ]

    # ── Example 2: Hard puzzle (requires significant backtracking) ──
    puzzle_hard = [
        [0, 0, 0,  0, 0, 0,  0, 0, 0],
        [0, 0, 0,  0, 0, 3,  0, 8, 5],
        [0, 0, 1,  0, 2, 0,  0, 0, 0],

        [0, 0, 0,  5, 0, 7,  0, 0, 0],
        [0, 0, 4,  0, 0, 0,  1, 0, 0],
        [0, 9, 0,  0, 0, 0,  0, 0, 0],

        [5, 0, 0,  0, 0, 0,  0, 7, 3],
        [0, 0, 2,  0, 1, 0,  0, 0, 0],
        [0, 0, 0,  0, 4, 0,  0, 0, 9],
    ]

    # ── Example 3: "World's Hardest Sudoku" (Arto Inkala, 2012) ──
    puzzle_inkala = [
        [8, 0, 0,  0, 0, 0,  0, 0, 0],
        [0, 0, 3,  6, 0, 0,  0, 0, 0],
        [0, 7, 0,  0, 9, 0,  2, 0, 0],

        [0, 5, 0,  0, 0, 7,  0, 0, 0],
        [0, 0, 0,  0, 4, 5,  7, 0, 0],
        [0, 0, 0,  1, 0, 0,  0, 3, 0],

        [0, 0, 1,  0, 0, 0,  0, 6, 8],
        [0, 0, 8,  5, 0, 0,  0, 1, 0],
        [0, 9, 0,  0, 0, 0,  4, 0, 0],
    ]

    puzzles = [
        ("Medium Puzzle", puzzle_medium, True),   # Show logs for this one
        ("Hard Puzzle", puzzle_hard, False),
        ("Inkala's Hardest Puzzle", puzzle_inkala, False),
    ]

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   SUDOKU SOLVER — AC-3 + Backtracking (MRV/Degree/LCV)    ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    for name, puzzle, show_log in puzzles:
        print(f"\n{'━' * 60}")
        print(f"  🧩  {name}")
        print(f"{'━' * 60}")

        print_grid(puzzle, "Input:")

        solution, stats = solve(puzzle, log=show_log)

        if solution:
            print_grid(solution, "Solution:")

            valid = validate_solution(solution)
            print(f"  ✅ Valid: {valid}")
        else:
            print("  ❌ No solution found.")

        print(f"\n  📊 Statistics:")
        print(f"     Assignments attempted : {stats.assignments}")
        print(f"     Backtracks            : {stats.backtracks}")
        print(f"     AC-3 calls            : {stats.ac3_calls}")
        print(f"     Time elapsed          : {stats.elapsed * 1000:.2f} ms")


if __name__ == "__main__":
    main()
