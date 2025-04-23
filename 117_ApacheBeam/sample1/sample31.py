import os
import apache_beam as beam

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, "input.txt")
TARGET = os.path.join(ROOT, "output.txt")

def to_upper_case(text):
    return text.upper()

def run(input_path, output_path):
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "Read text" >> beam.io.ReadFromText(input_path)
            | "Uppercase" >> beam.Map(to_upper_case)
            | "Write text" >> beam.io.WriteToText(output_path, shard_name_template='')
        )

def main():
    run(SOURCE, TARGET)

if __name__ == '__main__':
    main()
