import os
import sys

from typing import Any
from pathlib import Path
import warnings
import loguru
import shutil

showwarning_ = warnings.showwarning

# ==============================================================================


def get_logger() -> Any:

    return loguru.logger


# ==============================================================================


def showwarning(message, *args, **kwargs) -> None:

    get_logger().warning(message)
    # showwarning_(message, *args, **kwargs)


# ==============================================================================


def init_logger(
    console_output: bool = True,
    logfile: bool = False,
    logfolder_path: Path = Path(".", "logs"),
    logfile_name: str = "log",
    level: str = "INFO",
    capture_warnings: bool = True,
) -> Any:
    """This function configures and returns a logger based in loguru.

    Parameters
    ----------
    console_output : bool, optional
        If True, generates a sink to the console, by default True
    logfile : bool, optional
        If True, generates a sink to a logfile, by default False
    logfolder_path : os.PathLike, optional
        Folder that will be stored the logfile, by default Path(".", "logs")
    logfile_name : str, optional
        Name for the logfile, by default "log"
    capture_warnings: bool, optional
        Whether to capture warnings from the warnings module

    Returns
    -------
    Any
        Returns the logger class
    """

    logger = loguru.logger
    logger.remove(0)

    handlers = []
    # move previous logs to a history folder
    for legacy_logs in logfolder_path.glob("*.log"):
        os.makedirs(legacy_logs.parent / "log_history", exist_ok=True)
        shutil.move(legacy_logs, legacy_logs.parent / "log_history" / legacy_logs.name)

    if logfile:
        handlers.append(
            dict(
                sink=str(logfolder_path) + "/" + logfile_name + "_{time}.log",
                enqueue=True,
                # serialize=True,
                backtrace=True,
                diagnose=True,
                catch=True,
            )
        )

    if console_output:
        handlers.append(
            dict(
                sink=sys.stderr,
                enqueue=True,
                backtrace=True,
                diagnose=True,
                catch=True,
                level=level,
            )
        )

    logger.configure(
        handlers=handlers,
        levels=[],
        extra=[],
        activation=[],
    )

    # Monkey patch the showwarning function to dump all the warnign information to logs
    if capture_warnings:
        warnings.showwarning = showwarning
