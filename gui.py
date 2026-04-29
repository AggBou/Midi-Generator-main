import flet as ft
from sequencer import Pattern
from playback import MidiPlayer
from midi_export import export_pattern
from midi_import import import_pattern
from presets import save_presets, load_presets
from settings import SettingsWindow
from settings_manager import load_settings, save_settings
import os

class DrumApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Drum Sequencer"
        self.page.scroll = "auto"
        
        # Load settings
        self.app_settings = load_settings()
        self.dark_mode = self.app_settings.get("dark_mode", True)
        self.apply_theme()

        self.patterns = []
        self.current_pattern = Pattern(16)
        self.patterns.append(self.current_pattern)
        self.bpm = 120
        self.player = MidiPlayer()
        self.steps_options = [16, 32, 64]
        self.settings_window = SettingsWindow(self)
        
        # Load saved sound paths
        sound_paths = self.app_settings.get("sound_paths", {})
        for note_str, path in sound_paths.items():
            note = int(note_str)
            if os.path.exists(path):
                self.player.samples[note] = path

        self.init_ui()

    def apply_theme(self):
        if self.dark_mode:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT

    def init_ui(self):
        self.page.window.maximized = True
        
        # Layouts
        self.left_column = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.START, expand=False)
        self.right_column = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        self.settings_column = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.START, expand=False, visible=False)
        self.grid_buttons = []

        # Delay creating FilePicker until it's actually needed. Some
        # clients (web) don't support FilePicker and will raise an
        # Unknown control error when the control is instantiated or
        # rendered. We'll create it lazily in `pick_sound_file`.
        self.file_picker = None
        self.file_picker_supported = False
        
        # Theme toggle button
        theme_btn = ft.IconButton(
            icon=ft.Icons.DARK_MODE if self.dark_mode else ft.Icons.LIGHT_MODE,
            on_click=self.toggle_theme,
            tooltip="Toggle Dark/Light Mode"
        )
        
        # Settings button
        settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            on_click=self.toggle_settings_panel,
            tooltip="Open Settings"
        )

        # Step selector
        self.step_selector = ft.Dropdown(
            options=[ft.dropdown.Option(str(s)) for s in self.steps_options],
            value=str(self.steps_options[0]),
            on_select=self.change_steps,
            width=200,
            text_size=16
        )
        self.left_column.controls.append(ft.Text("Steps per pattern:", size=18, weight="bold"))
        self.left_column.controls.append(self.step_selector)

        # BPM selector
        self.bpm_selector = ft.TextField(
            value=str(self.bpm),
            on_change=self.change_bpm,
            width=100,
            text_size=16,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT
        )
        self.left_column.controls.append(ft.Text("BPM:", size=18, weight="bold"))
        self.left_column.controls.append(self.bpm_selector)

        # Buttons
        self.left_column.controls.extend([
            ft.ElevatedButton("Random Pattern", on_click=self.random_pattern, width=250, height=50),
            ft.ElevatedButton("Euclidean Kick", on_click=self.euclidean_pattern, width=250, height=50),
            ft.ElevatedButton("Generate Fill", on_click=self.generate_fill, width=250, height=50),
            ft.ElevatedButton("Save Presets", on_click=self.save_presets, width=250, height=50),
            ft.ElevatedButton("Load Presets", on_click=self.load_presets, width=250, height=50),
            ft.ElevatedButton("Clear All", on_click=self.clear_all, width=250, height=50),
        ])

        # Grid and text area
        self.grid_container = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll="auto", height=400, width=1000)
        self.text_area = ft.TextField(multiline=True, height=150, width=500, text_size=14)
        self.right_column.controls.append(self.grid_container)
        self.right_column.controls.append(ft.Text("Pattern Text (k=s/h):", size=18, weight="bold"))
        self.right_column.controls.append(self.text_area)
        self.right_column.controls.append(ft.ElevatedButton("Update Grid from Text", on_click=self.update_grid_from_text, width=250, height=50))

        # Playback controls
        self.right_column.controls.append(
            ft.Row([
                ft.ElevatedButton("Play", on_click=self.play_pattern, width=150, height=50),
                ft.ElevatedButton("Stop", on_click=self.stop_pattern, width=150, height=50),
                ft.ElevatedButton("Export MIDI", on_click=self.export_midi, width=150, height=50),
                ft.ElevatedButton("Import MIDI", on_click=self.import_midi, width=150, height=50),
            ], alignment=ft.MainAxisAlignment.CENTER)
        )

        # Settings panel
        self.setup_settings_panel()

        # Add to page with centered layout
        main_row = ft.Row([self.left_column, self.right_column, self.settings_column], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, expand=True, spacing=30)
        header = ft.Row([ft.Text("Drum Sequencer", size=32, weight="bold"), ft.Container(expand=True), settings_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.page.add(header, ft.Container(
            content=main_row,
            alignment=ft.alignment.Alignment.CENTER,
            expand=True,
            padding=20
        ))
        self.update_grid()

    def update_grid(self, _=None):
        self.grid_container.controls.clear()
        self.grid_buttons = []
        rows = ["Kick", "Snare", "Hi-hat"]
        for r in range(3):
            row_buttons = []
            row = ft.Row()
            for c in range(self.current_pattern.steps):
                btn = ft.Checkbox(value=self.current_pattern.grid[r][c], on_change=lambda e, x=r, y=c: self.toggle_step(x, y), scale=1.5)
                row.controls.append(btn)
                row_buttons.append(btn)
            self.grid_container.controls.append(row)
            self.grid_buttons.append(row_buttons)
        self.text_area.value = "\n".join(self.current_pattern.to_text())
        self.page.update()

    def toggle_theme(self, _):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.page.update()

    def toggle_theme_from_settings(self, e):
        """Toggle theme from settings switch"""
        self.dark_mode = e.control.value
        self.apply_theme()
        self.save_app_settings()
        self.page.update()

    def setup_settings_panel(self):
        """Setup the settings panel"""
        import os
        
        self.settings_column.controls.append(ft.Text("Settings", size=20, weight="bold"))
        self.settings_column.controls.append(ft.Divider())
        
        # Theme section
        self.settings_column.controls.append(ft.Text("Theme", size=16, weight="bold"))
        self.settings_column.controls.append(
            ft.Row([
                ft.Text("Dark Mode:", size=14),
                ft.Switch(
                    value=self.dark_mode,
                    on_change=self.toggle_theme_from_settings
                )
            ], spacing=10)
        )
        
        self.settings_column.controls.append(ft.Divider())
        
        # Sound settings section
        self.settings_column.controls.append(ft.Text("Sound Settings", size=16, weight="bold"))
        self.settings_column.controls.append(ft.Text("Select custom sounds:", size=12))
        
        # Get sound files
        sound_folder = "sounds"
        sound_files = {}
        if os.path.exists(sound_folder):
            for file in os.listdir(sound_folder):
                if file.endswith('.wav'):
                    sound_files[file] = os.path.join(sound_folder, file)
        
        # Create dropdowns for each drum
        self.create_sound_dropdowns(sound_files)
        
        self.settings_column.controls.append(ft.Divider())
        self.settings_column.controls.append(
            ft.ElevatedButton("Save Settings", on_click=self.toggle_settings_panel, width=200, height=40)
        )

    def create_sound_dropdowns(self, sound_files):
        """Create sound selection dropdowns"""
        from playback import NOTE_KICK, NOTE_SNARE, NOTE_HH
        
        drum_types = [
            ("Kick", "kick", NOTE_KICK),
            ("Snare", "snare", NOTE_SNARE),
            ("Hi-Hat", "hihat", NOTE_HH)
        ]
        
        for label, sound_type, note in drum_types:
            options = [ft.dropdown.Option("Default")]
            for file in sorted(sound_files.keys()):
                options.append(ft.dropdown.Option(file))
            
            dropdown = ft.Dropdown(
                label=f"Select {label}",
                options=options,
                width=200,
                text_size=12,
                on_select=lambda e, st=sound_type, sf=sound_files: self.change_sound(st, e, sf)
            )
            
            browse_btn = ft.ElevatedButton(
                "Browse",
                width=80,
                height=40,
                on_click=lambda e, st=sound_type: self.pick_sound_file(st)
            )
            
            self.settings_column.controls.append(
                ft.Row([
                    ft.Text(f"{label}:", size=12, width=80),
                    dropdown,
                    browse_btn
                ], spacing=5)
            )

    def change_sound(self, sound_type, e, sound_files):
        """Change sound for a drum type"""
        from playback import NOTE_KICK, NOTE_SNARE, NOTE_HH, SOUND_MAP
        
        notes = {
            "kick": NOTE_KICK,
            "snare": NOTE_SNARE,
            "hihat": NOTE_HH
        }
        
        selected_file = e.control.value
        note = notes.get(sound_type, 36)
        
        if selected_file == "Default":
            if note in SOUND_MAP:
                if os.path.exists(SOUND_MAP[note]):
                    self.player.samples[note] = SOUND_MAP[note]
        else:
            sound_path = sound_files.get(selected_file)
            if sound_path and os.path.exists(sound_path):
                self.player.samples[note] = sound_path
        
        self.save_app_settings()

    def toggle_settings_panel(self, _):
        """Toggle settings panel visibility"""
        self.settings_column.visible = not self.settings_column.visible
        self.page.update()

    def save_app_settings(self):
        """Save app settings to file"""
        # Convert player.samples dict to string keys for JSON
        sound_paths = {}
        for note, path in self.player.samples.items():
            sound_paths[str(note)] = path
        
        save_settings(self.dark_mode, sound_paths)

    def pick_sound_file(self, sound_type):
        """Open file picker to select sound file from PC"""
        self.current_sound_type = sound_type
        # Try to create FilePicker lazily (may fail on unsupported clients)
        if not self.file_picker and not self.file_picker_supported:
            try:
                self.file_picker = ft.FilePicker(on_upload=self.on_file_pick_result)
                try:
                    self.page.overlay.append(self.file_picker)
                except Exception:
                    # appending to overlay may fail on some clients
                    pass
                self.file_picker_supported = True
            except Exception:
                self.file_picker = None
                self.file_picker_supported = False

        if self.file_picker_supported and self.file_picker:
            try:
                self.file_picker.pick_files(allowed_extensions=["wav"])
            except Exception:
                self.page.snack_bar = ft.SnackBar(ft.Text("File picker not available in this client."))
                self.page.snack_bar.open = True
                self.page.update()
        else:
            # Fallback: instruct user to place .wav files into the `sounds/` folder
            self.page.snack_bar = ft.SnackBar(ft.Text("FilePicker not supported in this client. Place .wav files into the sounds/ folder and select them from the dropdown."))
            self.page.snack_bar.open = True
            self.page.update()

    def on_file_pick_result(self, e):
        """Handle file picker result"""
        if e.files:
            file_path = e.files[0].path
            if file_path.lower().endswith('.wav'):
                from playback import NOTE_KICK, NOTE_SNARE, NOTE_HH
                
                notes = {
                    "kick": NOTE_KICK,
                    "snare": NOTE_SNARE,
                    "hihat": NOTE_HH
                }
                
                sound_type = self.current_sound_type
                note = notes.get(sound_type, 36)
                self.player.samples[note] = file_path
                self.save_app_settings()
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Sound loaded: {os.path.basename(file_path)}"))
                self.page.snack_bar.open = True
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Please select a .wav file"))
                self.page.snack_bar.open = True
                self.page.update()

    def toggle_step(self, r, c):
        self.current_pattern.toggle(r, c)
        self.update_grid()

    def update_grid_from_text(self, _):
        text = self.text_area.value.splitlines()
        self.current_pattern.from_text(text)
        self.update_grid()

    def change_steps(self, e):
        steps = int(e.control.value)
        self.current_pattern.steps = steps
        self.current_pattern.grid = [[False] * steps for _ in range(3)]
        self.update_grid()

    def change_bpm(self, e):
        try:
            val = int(e.control.value)
            if val > 200:
                val = 200
                e.control.value = "200"
                e.control.update()
            
            self.bpm = val
        except ValueError:
            pass # Keep previous BPM if invalid

    def random_pattern(self, _):
        self.current_pattern.generate_random()
        self.update_grid()

    def euclidean_pattern(self, _):
        self.current_pattern.generate_euclidean(5, self.current_pattern.steps, 0)  # Kick
        self.update_grid()

    def generate_fill(self, _):
        self.current_pattern.generate_fill()
        self.update_grid()

    def play_pattern(self, _):
        self.player.play_pattern(self.current_pattern, self.bpm)

    def stop_pattern(self, _):
        self.player.stop()

    def export_midi(self, _):
        # Use native tkinter save dialog (Windows File Explorer style) to
        # ensure a visible save dialog opens for the user. This avoids
        # client-specific `ft.dialogs` behavior.
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            # Hide the root window but make the dialog topmost so it appears
            # in front of other windows (File Explorer / other apps).
            root.withdraw()
            root.update()
            root.attributes('-topmost', True)
            path = filedialog.asksaveasfilename(parent=root, defaultextension=".mid", filetypes=[("MIDI Files", "*.mid")], title="Export MIDI")
            root.attributes('-topmost', False)
            root.destroy()
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Export dialog failed: {type(e).__name__}: {e}"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        if not path:
            # user canceled
            return

        if not path.endswith('.mid'):
            path += '.mid'

        try:
            export_pattern([self.current_pattern], self.bpm, path)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Exported MIDI to {os.path.basename(path)}"))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Export error: {type(e).__name__}: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def import_midi(self, _):
        # Use native tkinter open dialog
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.update()
            root.attributes('-topmost', True)
            path = filedialog.askopenfilename(parent=root, filetypes=[("MIDI Files", "*.mid"), ("All Files", "*.*")], title="Import MIDI")
            root.attributes('-topmost', False)
            root.destroy()
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Import dialog failed: {type(e).__name__}: {e}"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        if not path:
            return

        try:
            pattern, bpm = import_pattern(path)
            if pattern:
                self.current_pattern = pattern
                self.patterns = [self.current_pattern] # Replace patterns list for now
                self.bpm = bpm
                
                # Update UI elements
                self.bpm_selector.value = str(self.bpm)
                self.step_selector.value = str(self.current_pattern.steps)
                
                # Refresh grid
                self.update_grid()
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Imported MIDI from {os.path.basename(path)}"))
                self.page.snack_bar.open = True
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Failed to import MIDI pattern"))
                self.page.snack_bar.open = True
                self.page.update()

        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Import error: {type(e).__name__}: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def clear_all(self, _):
        # Clear all steps in the current pattern and refresh UI
        self.current_pattern.grid = [[False] * self.current_pattern.steps for _ in range(3)]
        self.update_grid()

    def save_presets(self, _):
        save_presets(self.patterns)

    def load_presets(self, _):
        loaded = load_presets()
        if loaded:
            self.patterns = loaded
            self.current_pattern = self.patterns[0]
            self.update_grid()


def main(page: ft.Page):
    DrumApp(page)


if __name__ == "__main__":
    # When running gui.py directly, start a desktop Flet app.
    ft.run(main, view=ft.AppView.FLET_APP)