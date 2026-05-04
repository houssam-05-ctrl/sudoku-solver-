# Sudoku Solver CSP: AI Concepts and Project Overview

## Project Overview

This project is a full-stack application for solving Sudoku puzzles using artificial intelligence techniques, specifically Constraint Satisfaction Problem (CSP) methods. It features a Python (FastAPI) backend for the solving logic and a React frontend for user interaction.

## Educational Objective

The goal is to demonstrate how core AI concepts—such as problem modeling, state-space search, and constraint propagation—can be applied to a classic problem: Sudoku.

## AI Concepts Used

### 1. Constraint Satisfaction Problem (CSP)

A CSP is defined by:

- **Variables**: each cell in the Sudoku grid.
- **Domains**: for each variable, the set of possible values (1 to 9).
- **Constraints**: each row, column, and 3x3 block must contain distinct values.

### 2. Search and Backtracking

The solver uses backtracking search, a classic AI method for exploring the solution space. At each step, the algorithm:

- Selects an unassigned variable.
- Tries to assign a value consistent with the constraints.
- Backtracks if no value is possible.

### 3. AI Heuristics

To improve efficiency, several heuristics are used:

- **MRV (Minimum Remaining Values)**: choose the variable with the fewest legal values.
- **Forward Checking**: eliminate impossible values from neighboring variables' domains after each assignment.
- **AC-3 (Arc Consistency)**: enforce consistency between variables to reduce the search space.

### 4. Constraint Propagation

Constraint propagation quickly detects dead-ends and accelerates the search. It dynamically updates variable domains based on already satisfied constraints.

## Project Architecture

- **backend/**: FastAPI API, CSP solving logic in Python.
- **frontend/**: React interface for input and visualization of Sudoku solving.

## Conclusion

This project demonstrates the practical application of artificial intelligence to a combinatorial problem. It highlights the power of CSPs and intelligent search techniques to efficiently solve complex problems.

---

_Written by an AI professor and engineer._
