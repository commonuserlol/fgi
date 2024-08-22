from pathlib import Path
import subprocess

from fgi.logger import Logger


def run_command_and_check(cmd: list[str | Path]):
    try:
        Logger.debug(f"Running {cmd}")
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command {cmd} returned non-zero exit status: {e.output.decode()}")  # pyright: ignore[reportAny]
