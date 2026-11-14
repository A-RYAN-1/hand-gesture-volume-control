"""Background mode: global hotkeys and a small volume indicator, so the preview window is not needed.

Kept free of OpenCV, MediaPipe and pycaw imports at module level (tkinter and ctypes load only when the
indicator or the key reader is created), so the logic below can be tested without a webcam or Windows.
"""
VK_CONTROL = 0x11
VK_MENU = 0x12  # the Alt key


def virtual_key(char):
    """Windows virtual-key code of a letter or digit (the code of its capital)."""
    return ord(char.upper())


def windows_key_down(vk):
    """True while the key is held, whichever window has focus."""
    import ctypes

    return bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)


class HotkeyPoller:
    """Turns Ctrl+Alt+<key> presses into action names, once per press.

    Only the keys given and the two modifiers are ever read; nothing else the user types is seen.
    """

    def __init__(self, keys, is_down=windows_key_down):
        self.keys = keys  # action name -> virtual-key code
        self.is_down = is_down
        self._held = set()

    def poll(self):
        """Actions whose combination went down since the last call."""
        modifiers = self.is_down(VK_CONTROL) and self.is_down(VK_MENU)
        fired = []
        for action, vk in self.keys.items():
            down = modifiers and self.is_down(vk)
            if down and action not in self._held:
                fired.append(action)
            if down:
                self._held.add(action)
            else:
                self._held.discard(action)
        return fired


def indicator_text(percent, locked, muted):
    """The one line the indicator shows."""
    text = f"Volume {int(percent)}%"
    if locked:
        text += "  LOCKED"
    if muted:
        text += "  MUTED"
    return text


class ShowFor:
    """Visible for `seconds` after the text last changed, hidden after that."""

    def __init__(self, seconds):
        self.seconds = seconds
        self._text = None
        self._until = 0.0

    def visible(self, text, now):
        if text != self._text:
            self._text, self._until = text, now + self.seconds
        return now < self._until


class Indicator:
    """A small borderless window in the bottom-right corner, always on top, hidden when idle."""

    def __init__(self):
        import tkinter as tk

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.label = tk.Label(self.root, font=("Segoe UI", 14), fg="#ffffff", bg="#202020", padx=16, pady=8)
        self.label.pack()
        self.root.withdraw()
        self.shown = False

    def show(self, text):
        self.label.config(text=text)
        self.root.update_idletasks()
        x = self.root.winfo_screenwidth() - self.root.winfo_reqwidth() - 24
        y = self.root.winfo_screenheight() - self.root.winfo_reqheight() - 72
        self.root.geometry(f"+{x}+{y}")
        if not self.shown:
            self.root.deiconify()
            self.shown = True

    def hide(self):
        if self.shown:
            self.root.withdraw()
            self.shown = False

    def pump(self):
        """Let the window redraw; called once per camera frame."""
        self.root.update()

    def close(self):
        self.root.destroy()
