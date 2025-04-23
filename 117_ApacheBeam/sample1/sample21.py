import apache_beam as beam
import requests
import json

def step1(param1):
    print("this is step 1")
    print("param 1 : ",param1)

    return 1

def step2(param1):
    print("this is step 2")
    print("param 1 : ",param1)

    return 2

def step3(param1,param2):
    print("this is step 3")
    print("param 1 : ",param1)
    print("param 2 : ",param2)

    return [4, 5]

def step4(param1,param2):
    print("this is step 4")
    print("param 1 : ",param1)
    print("param 2 : ",param2)


def main():
    # print("---------- Case 1 ----------")
    # with beam.Pipeline() as pipeline:
    #     (
    #         pipeline
    #         | 'step 0' >> beam.Create(["param1"])
    #         | 'step 1' >> beam.Map(step1)
    #         | 'step 2' >> beam.Map(step2)
    #         | 'step 3' >> beam.Map(step3)　# This writing style is an error.
    #     )

    print("---------- Case 2 ----------")
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'step 0' >> beam.Create(["param1"])
            | 'step 1' >> beam.Map(step1)
            | 'step 2' >> beam.Map(step2)
            | 'step 3' >> beam.Map(lambda step2_ret: step3(step2_ret, 3))
        )

    print("---------- Case 3 ----------")
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'step 0' >> beam.Create(["param1"])
            | 'step 1' >> beam.Map(step1)
            | 'step 2' >> beam.Map(step2)
            | 'step 3' >> beam.Map(lambda step2_ret: step3(step2_ret, 3))
            | 'step 4' >> beam.Map(lambda step3_ret: step4(step3_ret[0], step3_ret[1]))
        )

if __name__ == "__main__":
    main()
