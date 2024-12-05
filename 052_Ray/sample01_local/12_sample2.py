import time
import inspect
import ray

# init ray
ray.init()

@ray.remote
class Counter(object):
    def __init__(self):
        self._counter = 0

    def getCounter(self):
        return self._counter

    def incCounter(self):
        self._counter += 1

def main():
    # Create an actor process.
    cnt = Counter.remote()

    print(ray.get(cnt.getCounter.remote()))  # 0
    cnt.incCounter.remote()
    cnt.incCounter.remote()
    print(ray.get(cnt.getCounter.remote()))  # 2

if __name__ == "__main__":
    main()
