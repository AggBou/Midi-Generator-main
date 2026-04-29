import flet as ft
import os
from pathlib import Path

class SettingsWindow:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.sound_files = self.get_sound_files()
        
    def get_sound_files(self):
        """Get all .wav files from sounds folder"""
        sound_folder = "sounds"
        if not os.path.exists(sound_folder):
            return {}
        
        files = {}
        for file in os.listdir(sound_folder):
            if file.endswith('.wav'):
                files[file] = os.path.join(sound_folder, file)
        return files
    
    def open_settings(self, _):
        """Open settings dialog"""
        dlg = ft.AlertDialog(
            title=ft.Text("Settings", size=24, weight="bold"),
            scrollable=True,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.close_dlg(e, dlg))
            ]
        )
        
        content = ft.Column(
            controls=[
                ft.Text("Theme", size=20, weight="bold"),
                ft.Row([
                    ft.Text("Dark Mode:", size=16),
                    ft.Switch(
                        value=self.parent_app.dark_mode,
                        on_change=self.parent_app.toggle_theme_from_settings
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                ft.Text("Sound Settings", size=20, weight="bold"),
                ft.Text("Select custom sounds from the sounds folder:", size=14),
                
                self.create_sound_selector("Kick", "kick"),
                self.create_sound_selector("Snare", "snare"),
                self.create_sound_selector("Hi-Hat", "hihat"),
            ],
            spacing=15,
            scroll="auto"
        )
        
        dlg.content = content
        self.parent_app.page.dialog = dlg
        dlg.open = True
        self.parent_app.page.update()
    
    def create_sound_selector(self, label, sound_type):
        """Create a dropdown for sound selection"""
        current_sound = self.parent_app.player.samples.get(self.get_note_for_type(sound_type), "Not set")
        
        options = [ft.dropdown.Option("Default")]
        for file in sorted(self.sound_files.keys()):
            options.append(ft.dropdown.Option(file))
        
        dropdown = ft.Dropdown(
            label=f"Select {label}",
            options=options,
            width=300,
            text_size=14,
            on_change=lambda e: self.change_sound(sound_type, e)
        )
        
        return ft.Row([
            ft.Text(f"{label}:", size=16, width=100),
            dropdown
        ], alignment=ft.MainAxisAlignment.START, spacing=10)
    
    def get_note_for_type(self, sound_type):
        """Get MIDI note number for sound type"""
        from playback import NOTE_KICK, NOTE_SNARE, NOTE_HH
        notes = {
            "kick": NOTE_KICK,
            "snare": NOTE_SNARE,
            "hihat": NOTE_HH
        }
        return notes.get(sound_type, 36)
    
    def change_sound(self, sound_type, e):
        """Change sound for a drum type"""
        selected_file = e.control.value
        if selected_file == "Default":
            # Reset to default
            from playback import SOUND_MAP
            note = self.get_note_for_type(sound_type)
            if note in SOUND_MAP:
                if os.path.exists(SOUND_MAP[note]):
                    self.parent_app.player.samples[note] = SOUND_MAP[note]
        else:
            # Use custom sound
            note = self.get_note_for_type(sound_type)
            sound_path = self.sound_files.get(selected_file)
            if sound_path and os.path.exists(sound_path):
                self.parent_app.player.samples[note] = sound_path
    
    def close_dlg(self, e, dlg):
        dlg.open = False
        self.parent_app.page.update()
