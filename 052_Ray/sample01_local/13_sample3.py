import os
import time
import inspect
import ray
import random

# init ray
ray.init()

@ray.remote
class Queue(object):
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        print(f"append value: {value}")
        self.queue.append(value)

    def dequeue(self):
        ret = None
        if self.queue:
            ret = self.queue.pop(0)
        print(f"pop value: {ret}")
        return ret

@ray.remote
def Input(queue):
    for idx in range(10):
        pid = os.getpid()
        print(f"Enqueue value: {pid}")
        queue.enqueue.remote(pid)
        time.sleep(random.randint(5, 10))
    return True

@ray.remote
def Output(queue):
    for _ in range(10):
        result = ray.get(queue.dequeue.remote())
        if result is not None:
            print(f"Dequeue value: {result}")
        time.sleep(random.randint(1, 5))
    return True

def main():
    # Create an actor process
    queue = Queue.remote()

    # Run Input and Output functions
    input1 = Input.remote(queue)
    input2 = Input.remote(queue)
    output = Output.remote(queue)

    # Wait for all tasks to complete
    results = ray.get([input1, input2, output])

    print(results)

if __name__ == "__main__":
    main()
