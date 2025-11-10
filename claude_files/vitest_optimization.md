# Vitest Optimization Guide

## Problem

Vitest was spawning 20+ worker processes consuming ~40% CPU each, causing system load to spike to 12+ and making the computer unresponsive.

## Root Causes

1. **Default Watch Mode**: Running `npm test` or `vitest` without `--run` flag starts vitest in watch mode, which:
   - Continuously monitors files for changes
   - Spawns worker processes equal to CPU cores (8-10 on your system)
   - Keeps processes running indefinitely

2. **Unlimited Workers**: By default, vitest spawns as many workers as CPU cores available, which can overwhelm the system when multiple test runs are active.

3. **Multiple Test Instances**: The orchestra subagent directories had test processes running simultaneously with the main project.

## Solutions Implemented

### 1. Limited Worker Processes

**File**: `frontend/vitest.config.js`

```javascript
poolOptions: {
  forks: {
    maxForks: 4,  // Limit to 4 workers max
    minForks: 1
  }
}
```

This limits vitest to spawn only 4 worker processes instead of 8-10.

### 2. Changed Default Test Command

**File**: `frontend/package.json`

**Before**:
```json
"test": "vitest"  // Runs in watch mode by default
```

**After**:
```json
"test": "vitest --run",        // One-time run, exits when done
"test:watch": "vitest",         // Explicit watch mode when needed
"test:coverage": "vitest --coverage --run"  // One-time with coverage
```

### 3. Applied to All Locations

Updated both:
- `/Users/wz/Desktop/zPersonalProjects/AICraft/frontend/`
- `/Users/wz/.orchestra/subagents/AICraft-frontend-tools/frontend/`

## Usage Guidelines

### Running Tests

**For one-time test runs** (recommended for most cases):
```bash
npm test
# or
npm run test:coverage
```

**For watch mode** (during active development):
```bash
npm run test:watch
```

**Important**: Always stop watch mode when done (Ctrl+C) to prevent runaway processes.

### Monitoring System Resources

Check for stuck vitest processes:
```bash
ps aux | grep vitest
```

Kill all vitest workers if stuck:
```bash
pkill -9 -f "vitest/dist/workers/forks.js"
```

## Performance Impact

**Before**:
- Load average: 12.12
- CPU usage: 72.74% system, 21.79% idle
- 20+ vitest workers running

**After**:
- Load average: ~2-3 (normal)
- CPU usage: 14.92% system, 78.15% idle
- Maximum 4 workers per test run

## Best Practices

1. **Always use `--run` flag** for CI/CD and one-time tests
2. **Limit watch mode** to active development sessions only
3. **Stop watch processes** when switching tasks or done coding
4. **Check for orphaned processes** if system slows down
5. **Consider using `test:ui`** for interactive testing instead of watch mode

## Additional Optimizations (Optional)

If tests are still slow, consider:

1. **Test file filtering**:
   ```bash
   vitest run src/components/  # Only test specific directory
   ```

2. **Reduce max workers further**:
   ```javascript
   maxForks: 2  // Even more conservative
   ```

3. **Use `--no-watch` flag explicitly**:
   ```bash
   vitest --no-watch
   ```

## Troubleshooting

**Q: Tests are still spawning too many processes**
- Check if multiple `npm test` commands are running
- Verify vitest.config.js has the poolOptions set
- Kill existing processes: `pkill -9 -f vitest`

**Q: Watch mode is too slow**
- Use `test:ui` instead for better control
- Filter tests to specific files
- Reduce maxForks to 2

**Q: Tests timeout in CI/CD**
- Ensure using `--run` flag
- Increase test timeout in vitest.config.js
- Check for infinite loops in tests
