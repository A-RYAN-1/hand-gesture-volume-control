from lock import VolumeLock


def test_starts_unlocked_and_follows_the_live_value():
    lock = VolumeLock()
    assert lock.locked is False
    assert lock.resolve(42.0) == 42.0


def test_locking_holds_the_value_from_the_moment_of_locking():
    lock = VolumeLock()
    assert lock.toggle(30.0) is True
    assert lock.resolve(90.0) == 30.0
    assert lock.resolve(0.0) == 30.0


def test_unlocking_follows_the_live_value_again():
    lock = VolumeLock()
    lock.toggle(30.0)
    assert lock.toggle(30.0) is False
    assert lock.resolve(75.0) == 75.0


def test_a_second_lock_holds_the_new_value():
    lock = VolumeLock()
    lock.toggle(30.0)
    lock.toggle(30.0)
    lock.toggle(60.0)
    assert lock.resolve(10.0) == 60.0
