import os
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import argparse
import time

class Step1Fn(beam.DoFn):
    def process(self, element):
        print("this is step 1")
        print(element)
        time.sleep(10)
        return [1]

class Step2Fn(beam.DoFn):
    def process(self, element):
        print("this is step 2")
        print(element)
        time.sleep(8)
        return [2]

class Step3Fn(beam.DoFn):
    def process(self, element):
        print("this is step 3")
        print(element)
        time.sleep(6)
        return [4, 5]

class Step4Fn(beam.DoFn):
    def process(self, element):
        print(element)
        print("this is step 4")
        time.sleep(4)
        return [6, 7]

with beam.Pipeline() as pipeline:
    (
        pipeline
        | 'step 0' >> beam.Create([("param1", "param2")])
        | 'step 1' >> beam.ParDo(Step1Fn())
        | 'step 2' >> beam.ParDo(Step2Fn())
        | 'step 3' >> beam.ParDo(Step3Fn())
        | 'step 4' >> beam.ParDo(Step4Fn())
    )
