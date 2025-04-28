from tika import parser
import os

os.environ['TIKA_SERVER'] = 'http://localhost:9997'

def main():
    directory = os.path.dirname(os.path.abspath(__file__))
    files = [
        "data.csv",
        "data.xlsx",
        "data.pdf",
    ]

    for file in files:
        print(f'========={file}=============')
        filepath = os.path.join(directory, file)

        # Load file data
        parsed = parser.from_file(filepath)
        print(parsed['content'])

        # Show metadata
        metadata = parsed["metadata"]
        for key, value in metadata.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
