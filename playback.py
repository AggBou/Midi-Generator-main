import time
import threading
import os
import playsound3

NOTE_KICK = 36
NOTE_SNARE = 38
NOTE_HH = 42

# Use absolute paths relative to this module so sounds are found regardless
# of the current working directory when the app is launched.
_BASE_DIR = os.path.dirname(__file__)
SOUND_MAP = {
    NOTE_KICK: os.path.join(_BASE_DIR, "sounds", "kick.wav"),
    NOTE_SNARE: os.path.join(_BASE_DIR, "sounds", "snare.wav"),
    NOTE_HH: os.path.join(_BASE_DIR, "sounds", "hihat.wav")
}

class MidiPlayer:
    def __init__(self):
        self.playing = False
        self.thread = None
        self.samples = {}

        # Store valid file paths
        for note, path in SOUND_MAP.items():
            if os.path.exists(path):
                self.samples[note] = path
            else:
                print(f"Warning: sound file not found: {path}")

    def send_note(self, note):
        path = self.samples.get(note)
        if path:
            # non-blocking playback
            playsound3.playsound(path, block=False)

    def play_pattern(self, pattern, bpm):
        if self.playing:
            return

        self.playing = True
        step_time = 60.0 / bpm / 4.0
        steps = pattern.steps
        events = pattern.get_events()

        print(step_time)

        def run():
            while self.playing:
                for step in range(steps):
                    
                    if not self.playing:
                        break
                    for note, c in events:
                        if c == step:
                            print(f"Playing step {step}")
                            self.send_note(note)
                    time.sleep(step_time)

        self.thread = threading.Thread(target=run)
        self.thread.start()

    def stop(self):
        self.playing = False
        if self.thread:
            self.thread.join()
            self.thread = None
