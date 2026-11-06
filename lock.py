"""Volume lock: holds the volume while locked, kept free of camera and audio imports so it can be tested."""


class VolumeLock:
    """Freezes the volume at the value it had when the lock was switched on."""

    def __init__(self):
        self.locked = False
        self._held = None

    def toggle(self, current_percent):
        """Switch the lock; locking remembers `current_percent`. Returns the new state."""
        self.locked = not self.locked
        self._held = current_percent if self.locked else None
        return self.locked

    def resolve(self, live_percent):
        """The percent to apply: the held value while locked, otherwise the live one."""
        return self._held if self.locked else live_percent
