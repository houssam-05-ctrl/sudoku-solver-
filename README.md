# AI Sudoku Solver: Constraint Satisfaction & Heuristic Search

## Project Overview

Welcome to the **AI Sudoku Solver**, a high-performance Python application designed to solve Sudoku puzzles using advanced Artificial Intelligence techniques. Rather than relying on simple brute-force trial and error, this solver models Sudoku as a **Constraint Satisfaction Problem (CSP)**. 

By leveraging the **AC-3 (Arc Consistency Algorithm #3)** for constraint propagation and intelligent backtracking with **Heuristic Search** strategies, this solver can crack even the most challenging Sudoku grids efficiently.

### Key Features
- **CSP Modeling**: Elegantly represents variables, domains, and constraints of a Sudoku grid.
- **Arc Consistency (AC-3)**: Pre-processes and continuously prunes the search space by eliminating invalid candidates early.
- **Intelligent Backtracking**: Employs heuristic-driven search to minimize the number of decisions and backtracks.
- **Zero Dependencies**: Built entirely using Python's standard library for maximum portability and ease of use.
- **Pedagogical Design**: Code is heavily documented and structured to serve as an educational resource for AI students and researchers.

---

## Underlying Concepts

This solver is built on foundational AI algorithms. Here is a breakdown of the core concepts utilized:

### 1. Constraint Satisfaction Problem (CSP)
A CSP is a mathematical framework defined by three components:
* **Variables ($X$)**: The 81 cells in a 9x9 Sudoku grid.
* **Domains ($D$)**: The possible values for each cell (typically digits 1-9).
* **Constraints ($C$)**: The rules of Sudoku—no duplicate digits are allowed in any row, column, or 3x3 subgrid.

### 2. AC-3 (Arc Consistency Algorithm #3)
Before and during the search process, AC-3 is used to enforce arc consistency. It examines pairs of connected variables (e.g., two cells in the same row). If assigning a value to Cell A leaves no valid options for Cell B, that value is removed from Cell A's domain. This drastic reduction in domains significantly shrinks the search space.

### 3. Heuristic Search Strategies
When AC-3 alone isn't enough to solve the puzzle, the algorithm falls back to search (backtracking). To make smart decisions on *which cell to fill next* and *which value to try first*, it uses three heuristics:

* **Minimum Remaining Values (MRV)**: Selects the cell with the fewest possible valid options left. This fail-first strategy quickly identifies dead ends.
* **Degree Heuristic**: Used as a tie-breaker for MRV. It selects the cell that is involved in the largest number of constraints with other unassigned cells, helping to reduce future choices.
* **Least Constraining Value (LCV)**: Once a cell is chosen, LCV determines the order of values to try. It picks the value that rules out the fewest choices for neighboring cells, maximizing flexibility.

---

## Installation & Setup

This project is lightweight and requires no external third-party libraries. 

### Prerequisites
- Python 3.8 or higher.

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/sudoku-solver-csp.git
   cd sudoku-solver-csp
   ```

2. **Verify Environment:**
   Ensure you are running the correct Python version:
   ```bash
   python --version
   ```

---

## 🚀 Usage Guide

You can run the solver directly from the command line. The solver accepts standard 81-character Sudoku strings where `0` or `.` represents an empty cell.

### Basic Execution

To run the solver with a default hardcoded puzzle or an interactive prompt (depending on the implementation):
```bash
python sudoku_solver.py
```

### Example Input / Output

**Input Representation (String):**
```text
003020600900305001001806400008102900700000008006708200002609500800203009005010300
```
*(You can also format this as a 2D array in the code).*

**Console Output:**
```text
--- Original Puzzle ---
. . 3 | . 2 . | 6 . . 
9 . . | 3 . 5 | . . 1 
. . 1 | 8 . 6 | 4 . . 
---------------------
. . 8 | 1 . 2 | 9 . . 
7 . . | . . . | . . 8 
. . 6 | 7 . 8 | 2 . . 
---------------------
. . 2 | 6 . 9 | 5 . . 
8 . . | 2 . 3 | . . 9 
. . 5 | . 1 . | 3 . . 

Solving using AC-3 + Backtracking...

--- Solved Puzzle ---
4 8 3 | 9 2 1 | 6 5 7 
9 6 7 | 3 4 5 | 8 2 1 
2 5 1 | 8 7 6 | 4 9 3 
---------------------
5 4 8 | 1 3 2 | 9 7 6 
7 2 9 | 5 6 4 | 1 3 8 
1 3 6 | 7 9 8 | 2 4 5 
---------------------
3 7 2 | 6 8 9 | 5 1 4 
8 1 4 | 2 5 3 | 7 6 9 
6 9 5 | 4 1 7 | 3 8 2 

Solution found in 0.042 seconds.
```

---

## Code Structure

The project is encapsulated in a primary script to make it easy to drop into educational environments, but is logically separated into distinct functional areas.

```text
sudoku-solver-csp/
│
├── sudoku_solver.py      # Main application and core logic
└── README.md             # Project documentation (this file)
```

### Inside `sudoku_solver.py`
- **`SudokuCSP` Class / Data Structures**: Manages the state, variables, domains, and neighbor relationships (constraints) of the board.
- **`ac3(csp)`**: Implements the Arc Consistency algorithm. Manages the queue of arcs and reduces domains.
- **`backtracking_search(csp)`**: The core recursive search algorithm.
- **Heuristic Functions**: `select_unassigned_variable()` (implements MRV and Degree) and `order_domain_values()` (implements LCV).
- **Utility Functions**: Methods for parsing grid strings, printing the board elegantly, and validating final states.

---

## How It Works (Algorithm Flow)

1. **Initialization**: The initial grid is parsed. Empty cells are assigned a domain of `{1, 2, 3, 4, 5, 6, 7, 8, 9}`, while pre-filled cells have a domain of `{value}`.
2. **Initial AC-3**: The AC-3 algorithm runs immediately to propagate the constraints of the pre-filled numbers. This usually solves simple puzzles entirely without any guessing.
3. **Check Status**: 
   - If all domains have size 1, the puzzle is solved.
   - If any domain has size 0, the puzzle is unsolvable.
   - If domains have multiple values, proceed to search.
4. **Backtracking Search**:
   - **Select Variable**: Use MRV + Degree heuristic to pick the best empty cell.
   - **Select Value**: Use LCV to try the best number for that cell.
   - **Assign & Propagate**: Assign the value and run a localized AC-3 (or forward checking) to ensure future consistency.
   - **Recurse**: Move to the next variable. If a dead end is reached, backtrack, undo the assignment, and try the next value.
5. **Termination**: The search returns a complete, valid assignment.

---

## Performance & Limitations

### Performance
- **Time Complexity**: While general Sudoku is NP-Complete, the application of AC-3 and MRV/LCV drastically reduces the empirical time complexity. Most standard 9x9 puzzles are solved in milliseconds.
- **Space Complexity**: $O(N^2 \times D)$ where $N=81$ variables and $D=9$ domain values, making it highly memory efficient.

### Limitations
- **Extreme Puzzles**: Puzzles specifically designed to defeat heuristic algorithms (e.g., puzzles requiring extensive logic like X-Wings or Swordfishes before any eliminations can occur) may force the solver to rely more heavily on deep backtracking, increasing solve time.
- **Scalability**: While highly optimized for 9x9 grids, scaling this specific implementation to 16x16 or 25x25 grids without structural optimizations will show performance degradation.

### Potential Improvements
- Implement **Naked Twins / Hidden Singles** deduction logic to supplement AC-3.
- Integrate **Dancing Links (DLX)** for exact cover formulation to compare performance against the CSP approach.
- Add an interactive GUI or web interface for visual algorithm execution.

---

## Contributing

Contributions, issues, and feature requests are welcome! 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Acknowledgments

* Artificial Intelligence: A Modern Approach by Stuart Russell and Peter Norvig (for foundational CSP concepts).
* The open-source AI community for continuous inspiration on heuristic optimization.
# sudoku-solver-
