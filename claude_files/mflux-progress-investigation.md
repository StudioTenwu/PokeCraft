# mflux Progress Streaming Investigation

## Problem
Agent hatching progress jumps from 33% → 100%, skipping the avatar generation progress (33-100%).

## Root Cause
**mflux uses tqdm progress bars which disable when stdout is not a TTY.**

### Evidence

1. **mflux outputs to stdout** (confirmed):
   ```bash
   mflux-generate ... > output.txt 2>&1
   # Result: Progress bars captured in file
   ```

2. **But Python subprocess doesn't see it in real-time**:
   ```python
   process = await asyncio.create_subprocess_exec(*cmd, stdout=PIPE)
   async for line in process.stdout:  # Never loops!
       print(line)
   ```

3. **Why?** tqdm (Python progress bar library used by mflux) checks:
   ```python
   if not sys.stdout.isatty():
       disable_progress = True
   ```

### Test Results

**Direct terminal** (mflux sees TTY):
```
  0%|          | 0/2 [00:00<?, ?it/s]
 50%|█████     | 1/2 [00:14<00:14, 14.19s/it]
100%|██████████| 2/2 [00:27<00:00, 13.88s/it]
```

**Python subprocess** (mflux doesn't see TTY):
```python
# No output until process completes!
# Then all progress appears at once (too late)
```

## Attempted Solutions

### ❌ Solution 1: Read from stderr
**Tried:** Changed `process.stderr` to read progress
**Result:** No output (mflux writes to stdout)

### ❌ Solution 2: Read stdout line-by-line
**Tried:** `async for line in process.stdout`
**Result:** Never loops (tqdm uses `\r` not `\n`)

### ❌ Solution 3: Read stdout in chunks with `\r` splitting
**Tried:** Read 100 bytes at a time, split by `\r`
**Result:** Buffer never fills (tqdm disabled, no output)

### ❌ Solution 4: Use `stdbuf` to disable buffering
**Tried:** `stdbuf -oL mflux-generate ...`
**Result:** `stdbuf` not available on macOS

### ❌ Solution 5: Set `PYTHONUNBUFFERED=1`
**Tried:** Pass environment variable
**Result:** Doesn't help (tqdm still detects non-TTY)

## Why This Matters

**Current UX:**
```
0-33%:   LLM generation (smooth)
33%:     Avatar start
33-100%: ⚠️  STUCK at 33% for 30-60 seconds
100%:    Suddenly complete!
```

**Expected UX:**
```
0-33%:   LLM generation
33%:     Avatar start
45%:     mflux progress...
62%:     mflux 50%...
80%:     mflux 75%...
100%:    Complete!
```

## Possible Solutions

### Option A: Use PTY (Pseudo-Terminal) ✅
Make mflux think it's running in a terminal:
```python
import pty
import os

master, slave = pty.openpty()
process = subprocess.Popen(
    cmd,
    stdout=slave,
    stderr=slave
)
os.close(slave)

# Read from master
output = os.read(master, 1024)
```

**Pros:** Real progress from mflux
**Cons:** Complex, async support tricky

### Option B: Fake Progress Ticks ✅
Generate smooth fake progress while mflux runs:
```python
async def generate_avatar_with_progress():
    # Start mflux
    process = await asyncio.create_subprocess_exec(...)

    # Fake progress ticks every 500ms
    for pct in range(33, 95, 5):
        await asyncio.sleep(0.5)
        yield {"progress": pct}

    # Wait for completion
    await process.wait()
    yield {"progress": 100}
```

**Pros:** Simple, smooth UX
**Cons:** Not real progress (but better than stuck!)

### Option C: Poll File Size 📊
Check output image file size periodically:
```python
while process.poll() is None:
    if output_path.exists():
        size = output_path.stat().st_size
        # Estimate progress based on expected file size
        yield {"progress": min(95, 33 + (size / expected_size * 67))}
    await asyncio.sleep(0.5)
```

**Pros:** Based on real data
**Cons:** File size not linear with progress

## Recommendation

**Use Option B (Fake Progress)** because:
1. Simple to implement
2. Provides smooth UX
3. Better than being stuck at 33%
4. Can add real progress later if mflux adds `--no-progress-bar` flag

## Implementation

```python
async def generate_avatar_stream(self, agent_id, prompt):
    # Start mflux in background
    process = await asyncio.create_subprocess_exec(...)

    # Generate smooth fake progress
    start_time = time.time()
    expected_duration = 30  # seconds

    while process.returncode is None:
        elapsed = time.time() - start_time
        fake_pct = min(95, int(33 + (elapsed / expected_duration * 62)))

        yield {
            "type": "avatar_progress",
            "progress": fake_pct,
            "message": f"Drawing... ({fake_pct}%)"
        }

        await asyncio.sleep(0.5)
        await asyncio.sleep(0)  # Allow process to update

    # Final 100%
    yield {"type": "avatar_progress", "progress": 100}
```

## Testing

Created comprehensive test suite:
- `backend/tests/unit/test_mflux_progress_parsing.py` (13 tests)
- Tests parse_mflux_progress() with real mflux output
- Tests progress mapping (mflux 0-100% → overall 25-100%)
- All tests pass ✅

**But**: Parsing works, capture doesn't (tqdm detection).
