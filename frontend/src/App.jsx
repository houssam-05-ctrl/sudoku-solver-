import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_URL = "http://localhost:8000";

const PUZZLES = {
  Easy: [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9]
  ],
  Hard: [
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,3,0,8,5],
    [0,0,1,0,2,0,0,0,0],
    [0,0,0,5,0,7,0,0,0],
    [0,0,4,0,0,0,1,0,0],
    [0,9,0,0,0,0,0,0,0],
    [5,0,0,0,0,0,0,7,3],
    [0,0,2,0,1,0,0,0,0],
    [0,0,0,0,4,0,0,0,9]
  ],
  Inkala: [
    [8,0,0,0,0,0,0,0,0],
    [0,0,3,6,0,0,0,0,0],
    [0,7,0,0,9,0,2,0,0],
    [0,5,0,0,0,7,0,0,0],
    [0,0,0,0,4,5,7,0,0],
    [0,0,0,1,0,0,0,3,0],
    [0,0,1,0,0,0,0,6,8],
    [0,0,8,5,0,0,0,1,0],
    [0,9,0,0,0,0,4,0,0]
  ]
};

const createEmptyGrid = () => Array.from({ length: 9 }, () => Array(9).fill(0));

function App() {
  const [grid, setGrid] = useState(createEmptyGrid());
  const [initialGrid, setInitialGrid] = useState(createEmptyGrid());
  const [animatedCells, setAnimatedCells] = useState(new Set()); // Solved cells
  const [invalidCells, setInvalidCells] = useState(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [toast, setToast] = useState(null);

  const cellRefs = useRef([]);

  useEffect(() => {
    cellRefs.current = cellRefs.current.slice(0, 81);
  }, []);

  const showToast = (msg, isError = false) => {
    setToast({ msg, isError });
    setTimeout(() => setToast(null), 3000);
  };

  const getLocalConflicts = (currentGrid) => {
    const invalid = new Set();
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const val = currentGrid[r][c];
        if (val === 0) continue;

        let conflict = false;
        // Check row
        for (let i = 0; i < 9; i++) {
          if (i !== c && currentGrid[r][i] === val) conflict = true;
        }
        // Check col
        for (let i = 0; i < 9; i++) {
          if (i !== r && currentGrid[i][c] === val) conflict = true;
        }
        // Check box
        const br = Math.floor(r / 3) * 3;
        const bc = Math.floor(c / 3) * 3;
        for (let i = br; i < br + 3; i++) {
          for (let j = bc; j < bc + 3; j++) {
            if ((i !== r || j !== c) && currentGrid[i][j] === val) conflict = true;
          }
        }
        if (conflict) invalid.add(`${r}-${c}`);
      }
    }
    return invalid;
  };

  const checkValidationLocal = (currentGrid) => {
    const invalid = getLocalConflicts(currentGrid);
    setInvalidCells(invalid);
    return invalid.size === 0;
  };

  const handleCellChange = (r, c, val) => {
    if (initialGrid[r][c] !== 0) return;
    const newGrid = grid.map(row => [...row]);
    
    // Only accept digits 1-9 or empty
    const num = parseInt(val, 10);
    if (isNaN(num) || num < 1 || num > 9) {
      newGrid[r][c] = 0;
    } else {
      newGrid[r][c] = num;
    }
    
    setGrid(newGrid);
    checkValidationLocal(newGrid);
    
    // Auto-advance cursor
    if (!isNaN(num) && num >= 1 && num <= 9) {
      const nextIdx = r * 9 + c + 1;
      if (nextIdx < 81) {
        cellRefs.current[nextIdx]?.focus();
      }
    }
  };

  const handleKeyDown = (e, r, c) => {
    const idx = r * 9 + c;
    if (e.key === 'ArrowRight' && c < 8) cellRefs.current[idx + 1]?.focus();
    else if (e.key === 'ArrowLeft' && c > 0) cellRefs.current[idx - 1]?.focus();
    else if (e.key === 'ArrowDown' && r < 8) cellRefs.current[idx + 9]?.focus();
    else if (e.key === 'ArrowUp' && r > 0) cellRefs.current[idx - 9]?.focus();
    else if (e.key === 'Backspace' && grid[r][c] === 0 && c > 0) {
      cellRefs.current[idx - 1]?.focus();
    }
  };

  const loadExample = (e) => {
    const level = e.target.value;
    if (PUZZLES[level]) {
      const puz = JSON.parse(JSON.stringify(PUZZLES[level]));
      setGrid(puz);
      setInitialGrid(JSON.parse(JSON.stringify(puz)));
      setAnimatedCells(new Set());
      setInvalidCells(new Set());
      setStats(null);
    }
    e.target.value = ""; // Reset dropdown
  };

  const clearGrid = () => {
    const empty = createEmptyGrid();
    setGrid(empty);
    setInitialGrid(empty);
    setAnimatedCells(new Set());
    setInvalidCells(new Set());
    setStats(null);
  };

  const validateGrid = async () => {
    // If backend is down, we fallback to local validation
    try {
      setIsLoading(true);
      const res = await fetch(`${API_URL}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grid })
      });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      
      const localValid = checkValidationLocal(grid);
      if (data.valid && localValid) {
        showToast("✅ Grid is valid so far!");
      } else {
        showToast("❌ Conflicts detected", true);
      }
    } catch (err) {
      console.error(err);
      const localValid = checkValidationLocal(grid);
      if (localValid) showToast("✅ Grid is valid (Offline Mode)");
      else showToast("❌ Conflicts detected (Offline Mode)", true);
    } finally {
      setIsLoading(false);
    }
  };

  const solvePuzzle = async () => {
    if (!checkValidationLocal(grid)) {
      showToast("❌ Fix conflicts before solving", true);
      return;
    }

    try {
      setIsLoading(true);
      setStats(null);
      setAnimatedCells(new Set());

      const res = await fetch(`${API_URL}/solve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grid })
      });
      
      if (!res.ok) throw new Error("Backend offline or error");
      const data = await res.json();

      if (!data.solution || !data.valid) {
        showToast("❌ No solution found", true);
        setStats(data.stats);
        return;
      }

      setStats(data.stats);
      showToast(`✅ Solved in ${data.stats.elapsed_ms.toFixed(2)} ms`);
      animateSolution(data.solution);

    } catch (err) {
      console.error(err);
      showToast(`Error: ${err.message}`, true);
    } finally {
      setIsLoading(false);
    }
  };

  const animateSolution = (solGrid) => {
    const cellsToFill = [];
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        if (grid[r][c] === 0 && solGrid[r][c] !== 0) {
          cellsToFill.push({ r, c, val: solGrid[r][c] });
        }
      }
    }

    cellsToFill.forEach((cell, idx) => {
      setTimeout(() => {
        setGrid(prev => {
          const next = prev.map(row => [...row]);
          next[cell.r][cell.c] = cell.val;
          return next;
        });
        setAnimatedCells(prev => {
          const next = new Set(prev);
          next.add(`${cell.r}-${cell.c}`);
          return next;
        });
      }, idx * 50); // 50ms delay
    });
  };

  return (
    <div className="container">
      <header>
        <h1>AI Sudoku Solver</h1>
        <p>AC-3 + Heuristic Backtracking</p>
      </header>

      <main>
        <div className="board-container">
          <div className="sudoku-grid">
            {grid.map((row, r) => (
              row.map((val, c) => {
                const isInitial = initialGrid[r][c] !== 0;
                const isAnimated = animatedCells.has(`${r}-${c}`);
                const isInvalid = invalidCells.has(`${r}-${c}`);

                let className = "cell";
                if (isInitial) className += " initial";
                if (isAnimated) className += " solved";
                if (isInvalid) className += " invalid";

                // Thicker borders for boxes logic is in CSS
                return (
                  <input
                    key={`${r}-${c}`}
                    ref={el => cellRefs.current[r * 9 + c] = el}
                    type="text"
                    inputMode="numeric"
                    maxLength="1"
                    className={className}
                    value={val === 0 ? "" : val}
                    readOnly={isInitial || isLoading}
                    onChange={(e) => handleCellChange(r, c, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, r, c)}
                    onFocus={(e) => e.target.select()}
                  />
                );
              })
            ))}
          </div>

          <div className="controls">
            <div className="btn-group">
              <button className="primary" onClick={solvePuzzle} disabled={isLoading}>
                {isLoading ? <span className="spinner"></span> : "Solve"}
              </button>
              <button onClick={validateGrid} disabled={isLoading}>Validate</button>
              <button onClick={clearGrid} disabled={isLoading}>Clear</button>
            </div>
            
            <div className="dropdown-group">
              <select onChange={loadExample} defaultValue="" disabled={isLoading}>
                <option value="" disabled>Load Example...</option>
                <option value="Easy">Easy</option>
                <option value="Hard">Hard</option>
                <option value="Inkala">Inkala (Hardest)</option>
              </select>
            </div>
          </div>
        </div>

        {stats && (
          <div className="stats-panel">
            <h2>Solver Statistics</h2>
            <div className="stats-grid">
              <StatCard label="Assignments" value={stats.assignments} />
              <StatCard label="Backtracks" value={stats.backtracks} />
              <StatCard label="AC-3 Calls" value={stats.ac3_calls} />
              <StatCard label="Time" value={`${stats.elapsed_ms.toFixed(2)} ms`} isTime />
            </div>
          </div>
        )}
      </main>

      {toast && (
        <div className={`toast ${toast.isError ? 'error' : 'success'}`}>
          {toast.msg}
        </div>
      )}
    </div>
  );
}

const StatCard = ({ label, value, isTime = false }) => {
  const [displayVal, setDisplayVal] = useState(0);

  useEffect(() => {
    if (typeof value === 'string') {
      setDisplayVal(value);
      return;
    }
    
    let start = 0;
    const end = parseFloat(value);
    if (end === 0) {
      setDisplayVal(0);
      return;
    }

    const duration = 1000;
    const incrementTime = 20;
    const step = end / (duration / incrementTime);

    let timer = setInterval(() => {
      start += step;
      if (start >= end) {
        clearInterval(timer);
        setDisplayVal(end);
      } else {
        setDisplayVal(start);
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [value]);

  const formattedVal = isTime ? displayVal : Math.floor(displayVal);

  return (
    <div className="stat-card">
      <span className="stat-value">{formattedVal}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
};

export default App;
