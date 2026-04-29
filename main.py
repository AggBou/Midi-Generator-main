# main.py
import sys
import os
import ctypes
import enum
import flet as ft
from gui import main as flet_main

class SW(enum.IntEnum):

    HIDE = 0
    MAXIMIZE = 3
    MINIMIZE = 6
    RESTORE = 9
    SHOW = 5
    SHOWDEFAULT = 10
    SHOWMAXIMIZED = 3
    SHOWMINIMIZED = 2
    SHOWMINNOACTIVE = 7
    SHOWNA = 8
    SHOWNOACTIVATE = 4
    SHOWNORMAL = 1


class ERROR(enum.IntEnum):

    ZERO = 0
    FILE_NOT_FOUND = 2
    PATH_NOT_FOUND = 3
    BAD_FORMAT = 11
    ACCESS_DENIED = 5
    ASSOC_INCOMPLETE = 27
    DDE_BUSY = 30
    DDE_FAIL = 29
    DDE_TIMEOUT = 28
    DLL_NOT_FOUND = 32
    NO_ASSOC = 31
    OOM = 8
    SHARE = 26

if __name__ == "__main__":
    # Elevation removed: the app will no longer relaunch as admin.
    # If you need admin privileges later, handle them in specific routines.
    skip_elevate = True

    # Ensure Flet launches in the desktop Flet App view so desktop-only
    # controls like FilePicker are available in the client.
    ft.run(flet_main, view=ft.AppView.FLET_APP)


