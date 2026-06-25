import time
import threading
import os

try:
    import winsound
    _use_winsound = True
except ImportError:
    _use_winsound = False
    import playsound3

def _play_sound_async(path):
    if _use_winsound:
        winsound.PlaySound(path, winsound.SND_ASYNC)
    else:
        playsound3.playsound(path, block=False)

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
            _play_sound_async(path)

    def play_pattern(self, pattern, bpm):
        if self.playing:
            return

        self.playing = True
        step_time = 60.0 / bpm / 4.0
        steps = pattern.steps
        events = pattern.get_events()

        print(step_time)

        def run():
            import time
            start_time = time.perf_counter()
            step_index = 0
            while self.playing:
                target_time = start_time + step_index * step_time
                now = time.perf_counter()
                if now < target_time:
                    # Sleep most of the time, then busy-wait for final microseconds
                    time.sleep(max(0, target_time - now - 0.001))  # leave 1ms for busy-wait
                    # Busy-wait for remaining time
                    while time.perf_counter() < target_time:
                        pass
                if not self.playing:
                    break
                step = step_index % steps
                for note, c in events:
                    if c == step:
                        self.send_note(note)
                step_index += 1

        self.thread = threading.Thread(target=run)
        self.thread.start()

    def stop(self):
        self.playing = False
        if self.thread:
            self.thread.join()
            self.thread = None
