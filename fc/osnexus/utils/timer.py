# timer.py
# from: https://realpython.com/python-timer/

import time
from contextlib import ContextDecorator
from typing import Any


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer(ContextDecorator):
    """Time your code using a class, context manager, or decorator"""
    timers = dict()

    def __init__(
        self,
        name=None,
        def_stop_text="Elapsed time: {:0.4f} seconds",
        start_text=None,
        stop_text=None,
        logger=None,
    ):
        self._start_time = None
        self.name = name
        self.def_stop_text = def_stop_text
        self.start_text = start_text
        self.stop_text = stop_text
        self.logger = logger
        self._start_time = None

    def __post_init__(self) -> None:
        """Initialization: add timer to dict of timers"""
        if self.name:
            self.timers.setdefault(self.name, 0)

    def start(self, start_text=None) -> None:
        """Start a new timer"""
        if start_text:
            self.start_text = start_text

        if self.logger and self.start_text:
            self.logger(self.start_text)

        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def elapsed(self) -> float:
        return time.perf_counter() - self._start_time

    def stop(self, stop_text=None) -> float:
        """Stop the timer, and report the elapsed time"""

        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        # Report elapsed time
        if self.logger:
            if stop_text:
                self.stop_text = stop_text

            if self.stop_text:
                self.logger(self.stop_text.format(elapsed_time))
            else:
                self.logger(self.def_stop_text.format(elapsed_time))

        if self.name:
            self.timers[self.name] += elapsed_time

        return elapsed_time

    def __enter__(self) -> "Timer":
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """
        Stop the context manager timer only on exit if there is a logger configured
         as if there is no logger then there is no reason to compute elapsed_time
         for automatic printing; plus this gets around the context manager
         "TimerError: Timer is not running. Use .start() to start it" if stop
         is called within the context manager and the timer isn't restarted before
         the context manager exits.
        """
        if self.logger:
            self.stop()
