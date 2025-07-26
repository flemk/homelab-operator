import os

def is_process_running(pid_file):
    """Check if a process is running based on its PID file."""
    if not os.path.exists(pid_file):
        return False

    with open(pid_file, 'r') as f:
        pid = f.read().strip()

    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False
