import apache_beam as beam

def main():
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "1. create data" >> beam.Create(["Hello", "World"])
            | "2. print data"  >> beam.Map(print)
        )

if __name__ == '__main__':
    main()