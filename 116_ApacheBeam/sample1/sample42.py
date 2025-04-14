import os
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

class Task1(beam.DoFn):
    def process(self, element):
        print(f"[PID {os.getpid()}] This is Task 1")
        print(element)
        time.sleep(10)
        return [1]

class Task2(beam.DoFn):
    def process(self, element):
        print(f"[PID {os.getpid()}] This is Task 2")
        print(element)
        time.sleep(8)
        return [2]

class Task3(beam.DoFn):
    def process(self, element):
        print(f"[PID {os.getpid()}] This is Task 3")
        print(element)
        time.sleep(6)
        return [3]

class Task4(beam.DoFn):
    def process(self, element):
        print(f"[PID {os.getpid()}] This is Task 4")
        print(element)
        time.sleep(4)
        return [4]

def run_task_in_parallel(fn_class, element):
    """Run each task in parallel using ProcessPoolExecutor"""
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fn_class().process, element))
    # Flatten results
    return [item for sublist in results for item in sublist]

with beam.Pipeline() as pipeline:
    elements = ["Parameter A", "Parameter B"]

    # Task 1
    (
        pipeline
        | 'Task 1 - Start' >> beam.Create(elements)
        | 'Task 1 - Execute' >> beam.FlatMap(lambda element: run_task_in_parallel(Task1, [element]))
    )

    # Task 2
    (
        pipeline
        | 'Task 2 - Start' >> beam.Create(elements)
        | 'Task 2 - Execute' >> beam.FlatMap(lambda element: run_task_in_parallel(Task2, [element]))
    )

    # Task 3
    (
        pipeline
        | 'Task 3 - Start' >> beam.Create(elements)
        | 'Task 3 - Execute' >> beam.FlatMap(lambda element: run_task_in_parallel(Task3, [element]))
    )

    # Task 4
    (
        pipeline
        | 'Task 4 - Start' >> beam.Create(elements)
        | 'Task 4 - Execute' >> beam.FlatMap(lambda element: run_task_in_parallel(Task4, [element]))
    )
