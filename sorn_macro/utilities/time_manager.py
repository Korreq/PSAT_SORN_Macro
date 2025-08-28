import time
from datetime import datetime, timezone, timedelta

class TimeManager:
    '''Utility for generating UTC timestamps and measuring elapsed time.'''

    def __init__(self):
        # Use a monotonic clock to avoid issues if system time changes
        self._start = time.perf_counter()

    @staticmethod
    def get_current_utc_time(fmt: str = "%Y-%m-%d--%H-%M-%S", utc = False) -> str:
        '''Return the current UTC time as a formatted string. 
        Default time format is: 2025-01-01--01-00-00 .'''

        return datetime.now(timezone.utc).strftime(fmt) if utc else datetime.now().strftime(fmt)


    def elapsed_time(self) -> str:
        '''Compute time elapsed since instantiation and return it in a zero-padded "HH:MM:SS" string.'''
        
        elapsed = time.perf_counter() - self._start
        delta = timedelta(seconds=round(elapsed))

        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
