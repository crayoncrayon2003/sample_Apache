import apache_beam as beam

def mul_two(x):
    return x * 2

def add_one(x):
    return x + 1

def main():
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "1. create numbers" >> beam.Create([1, 2, 3, 4, 5])
            | "2. multiply by two" >> beam.Map(mul_two)
            | "3. add ten" >> beam.Map(add_one)
            | "4. print results" >> beam.Map(print)
        )

if __name__ == '__main__':
    main()