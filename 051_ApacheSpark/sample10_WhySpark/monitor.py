import time
import psutil
import os

class Monitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = None
        self.peak_memory = 0

    def start(self):
        self.start_time = time.time()
        self.peak_memory = 0
        self.sample()

    def sample(self):
        # Get memory usage (in MB)
        mem_info = self.process.memory_info()
        current_mem = mem_info.rss / 1024 / 1024
        if current_mem > self.peak_memory:
            self.peak_memory = current_mem

    def stop(self):
        elapsed = time.time() - self.start_time
        return elapsed, self.peak_memory