import mido
from sequencer import Pattern, NOTE_KICK, NOTE_SNARE, NOTE_HH

def import_pattern(filename):
    try:
        mid = mido.MidiFile(filename)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return None, 120

    # Determine BPM (default 120)
    bpm = 120
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                bpm = int(mido.tempo2bpm(msg.tempo))
                break
    
    # Grid mapping
    # Kick: 35 (Acoustic Bass Drum), 36 (Bass Drum 1)
    # Snare: 38 (Acoustic Snare), 40 (Electric Snare)
    # Hi-Hat: 42 (Closed HH), 44 (Pedal HH), 46 (Open HH)
    NOTE_MAP = {
        35: 0, 36: 0,
        38: 1, 40: 1,
        42: 2, 44: 2, 46: 2
    }
    
    # Find active steps
    hits = []  # List of (step_index, row_index)
    
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_step = ticks_per_beat / 4
    
    max_step = 15 # Minimum 16 steps
    
    for track in mid.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                if msg.note in NOTE_MAP:
                    step = int(round(abs_time / ticks_per_step))
                    hits.append((step, NOTE_MAP[msg.note]))
                    if step > max_step:
                        max_step = step

    # Determine pattern length (nearest multiple of 16)
    pattern_steps = max_step + 1
    if pattern_steps % 16 != 0:
        pattern_steps = ((pattern_steps // 16) + 1) * 16
        
    pattern = Pattern(pattern_steps)
    
    # Fill grid
    for step, row in hits:
        if step < pattern_steps:
            pattern.grid[row][step] = True
            
    return pattern, bpm
