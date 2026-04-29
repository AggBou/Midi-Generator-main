# sequencer.py
import random
import math

NOTE_KICK = 36
NOTE_SNARE = 38
NOTE_HH = 42

NOTE_MAP = {
    "k": NOTE_KICK,
    "s": NOTE_SNARE,
    "h": NOTE_HH
}

class Pattern:
    def __init__(self, steps=16):
        self.steps = steps
        self.grid = [[False] * steps for _ in range(3)]  # Kick, Snare, Hat

    # Convert pattern to text rows (k s h or .)
    def to_text(self):
        rows = []
        for r in range(3):
            row = ""
            for c in range(self.steps):
                row += "ksh"[r] if self.grid[r][c] else "."
            rows.append(row)
        return rows

    # Load pattern from text
    def from_text(self, text_rows):
        for r, row in enumerate(text_rows):
            for c, ch in enumerate(row[:self.steps]):
                self.grid[r][c] = (
                    ch.lower() in ["k", "s", "h"] and "ksh".index(ch.lower()) == r
                )

    # Toggle a step
    def toggle(self, row, col):
        self.grid[row][col] = not self.grid[row][col]

    # Random pattern (25% chance per step)
    def generate_random(self):
        for r in range(3):
            for c in range(self.steps):
                self.grid[r][c] = (random.random() < 0.25)

    # "Fill" pattern (snare 50%, others 30%)
    def generate_fill(self):
        for r in range(3):
            for c in range(self.steps):
                self.grid[r][c] = (random.random() < (0.5 if r == 1 else 0.3))

    def generate_euclidean(self, pulses, total, row):
        """Generate Euclidean rhythm using the Bjorklund algorithm."""
        # Safety edge cases
        if pulses <= 0:
            self.grid[row] = [False] * total
            return
        if pulses >= total:
            self.grid[row] = [True] * total
            return

        # Step 1: initialization
        counts = []
        remainders = [pulses]
        divisor = total - pulses
        level = 0

        # Step 2: compute counts/remainders
        while True:
            counts.append(divisor // remainders[level])
            remainders.append(divisor % remainders[level])
            divisor = remainders[level]
            level += 1
            if remainders[level] == 0:
                break

        # Step 3: recursion build
        def build(lv):
            if lv < 0:
                return []
            seq = []
            for _ in range(counts[lv]):
                seq.extend(build(lv - 1))
            if remainders[lv] != 0:
                seq.extend(build(lv - 2))
            return seq

        # Ensure we're not going out of bounds with the build process
        pattern = build(level - 1)  # Adjust level to match counts index

        # Normalize to exact length
        pattern = pattern[:total]
        while len(pattern) < total:
            pattern.append(0)

        # Apply pattern to grid (1 = hit)
        for c in range(total):
            self.grid[row][c] = (pattern[c] == 1)

    # Return list of (note, step)
    def get_events(self):
        events = []
        for r, note in enumerate([NOTE_KICK, NOTE_SNARE, NOTE_HH]):
            for c in range(self.steps):
                if self.grid[r][c]:
                    events.append((note, c))
        return events
