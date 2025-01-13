import os
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, "input.txt")
TARGET = os.path.join(ROOT, "output.txt")

def to_upper_case(text):
    return text.upper()

class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            "--input",
            help="Path of the input file to read from",
            default=SOURCE,
        )
        parser.add_argument(
            "--output",
            help="Path of the output file to write to",
            default=TARGET,
        )


def run(input_path, output_path, pipeline_options=None):
    with beam.Pipeline(options=pipeline_options) as pipeline:
        (
            pipeline
            | "Read text" >> beam.io.ReadFromText(input_path)
            | "Uppercase" >> beam.Map(to_upper_case)
            | "Write text" >> beam.io.WriteToText(output_path, shard_name_template='')  # シャード名を制御
        )

def main():
    pipeline_options = PipelineOptions()
    custom_options = pipeline_options.view_as(CustomOptions)

    # 引数を使って run を呼び出し
    run(
        input_path=custom_options.input,
        output_path=custom_options.output,
        pipeline_options=pipeline_options,
    )

if __name__ == '__main__':
    main()
