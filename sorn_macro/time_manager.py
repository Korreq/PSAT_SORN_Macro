from datetime import datetime, timezone
import time

class TimeManager:

    def __init__(self):
        self.timer = time.time()


    def get_current_utc_time(self):

        return datetime.now(timezone.utc).strftime('%Y-%m-%d--%H-%M-%S')


    def elapsed_time(self):

        time_difference = round( time.time() - self.timer )
        hours = minutes = 0

        hours = time_difference // 3600
        time_difference -= hours * 3600
        minutes = time_difference // 60
        time_difference -= minutes * 60
        
        return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(time_difference).zfill(2)}"
