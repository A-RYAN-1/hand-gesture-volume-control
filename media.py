"""Send the Windows play/pause media key, the same key a keyboard's play button sends.

Any player that listens for media keys (a browser tab, Spotify, VLC, the system media overlay) reacts to it,
so this tool needs no connection to a particular player. The key press is injected through `send_key` so the
tests can check it without touching the keyboard.
"""
import ctypes

VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_KEYUP = 0x0002


def _keybd_event(virtual_key, flags):
    ctypes.windll.user32.keybd_event(virtual_key, 0, flags, 0)


def toggle_play_pause(send_key=_keybd_event):
    """Press and release the play/pause media key."""
    send_key(VK_MEDIA_PLAY_PAUSE, 0)
    send_key(VK_MEDIA_PLAY_PAUSE, KEYEVENTF_KEYUP)
