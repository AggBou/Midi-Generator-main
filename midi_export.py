from mido import MidiFile, MidiTrack, Message
import mido

MAX_PARALLEL = 3

def export_pattern(patterns, bpm, filename):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    tempo = int(60_000_000 / bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    ppq = mid.ticks_per_beat
    step_ticks = ppq // 4  # 16th note resolution

    for pat in patterns:
        events = pat.get_events()
        steps = pat.steps

        for step in range(steps):
            # === COLLECT NOTES AT THIS STEP ===
            notes = [note for note, c in events if c == step]

            # === LIMIT TO MAX_PARALLEL ===
            notes = notes[:MAX_PARALLEL]

            if notes:
                # === NOTE ON (ALL AT SAME TIME) ===
                for n in notes:
                    track.append(Message(
                        'note_on',
                        channel=9,
                        note=n,
                        velocity=100,
                        time=0
                    ))

                # === ADVANCE TIME ONCE ===
                track.append(Message(
                    'note_off',
                    channel=9,
                    note=notes[0],
                    velocity=0,
                    time=step_ticks
                ))

                # === TURN OFF REST (NO TIME ADVANCE) ===
                for n in notes[1:]:
                    track.append(Message(
                        'note_off',
                        channel=9,
                        note=n,
                        velocity=0,
                        time=0
                    ))

            else:
                # no notes → just advance time
                track.append(Message(
                    'note_on',
                    channel=9,
                    note=36,
                    velocity=0,
                    time=step_ticks
                ))

    mid.save(filename)