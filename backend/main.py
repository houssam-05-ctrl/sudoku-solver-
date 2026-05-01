from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from solver import solve, validate_solution

app = FastAPI(title="Sudoku Solver API")

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GridInput(BaseModel):
    grid: List[List[int]]

class Stats(BaseModel):
    assignments: int
    backtracks: int
    ac3_calls: int
    elapsed_ms: float

class SolveResponse(BaseModel):
    solution: Optional[List[List[int]]]
    stats: Stats
    valid: bool

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/solve", response_model=SolveResponse)
def solve_grid(data: GridInput):
    if len(data.grid) != 9 or any(len(row) != 9 for row in data.grid):
        raise HTTPException(status_code=400, detail="Grid must be exactly 9x9")
    
    for row in data.grid:
        if any(val < 0 or val > 9 for val in row):
            raise HTTPException(status_code=400, detail="Values must be between 0 and 9")

    solution, stats = solve(data.grid, log=False)
    elapsed_ms = stats.elapsed * 1000

    if not solution:
        return SolveResponse(
            solution=None,
            stats=Stats(
                assignments=stats.assignments,
                backtracks=stats.backtracks,
                ac3_calls=stats.ac3_calls,
                elapsed_ms=elapsed_ms
            ),
            valid=False
        )

    return SolveResponse(
        solution=solution,
        stats=Stats(
            assignments=stats.assignments,
            backtracks=stats.backtracks,
            ac3_calls=stats.ac3_calls,
            elapsed_ms=elapsed_ms
        ),
        valid=validate_solution(solution)
    )

@app.post("/validate")
def validate_grid(data: GridInput):
    if len(data.grid) != 9 or any(len(row) != 9 for row in data.grid):
        raise HTTPException(status_code=400, detail="Grid must be exactly 9x9")
    
    # Partial validation for user input (checks for rule violations so far)
    valid = _partial_validation(data.grid)
    return {"valid": valid}

def _partial_validation(grid: List[List[int]]) -> bool:
    for r in range(9):
        seen = set()
        for c in range(9):
            val = grid[r][c]
            if val != 0:
                if val in seen: return False
                seen.add(val)

    for c in range(9):
        seen = set()
        for r in range(9):
            val = grid[r][c]
            if val != 0:
                if val in seen: return False
                seen.add(val)

    for box_r in range(0, 9, 3):
        for box_c in range(0, 9, 3):
            seen = set()
            for r in range(box_r, box_r + 3):
                for c in range(box_c, box_c + 3):
                    val = grid[r][c]
                    if val != 0:
                        if val in seen: return False
                        seen.add(val)
    return True
