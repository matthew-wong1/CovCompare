import json


def load_dict_from_file(file_path):
    """ Load JSON dictionary from a file. """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)['f']
    except FileNotFoundError:
        print("File not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return None


def main(fuzzer_coverage_path, cts_coverage_path):
    fuzzer_coverage_dict = load_dict_from_file(fuzzer_coverage_path)
    cts_coverage_dict = load_dict_from_file(cts_coverage_path)

    print(fuzzer_coverage_dict)

# File paths (replace these with the actual paths to your JSON files)
fuzzer_coverage_path = '/Users/matthew/Documents/msc/final_proj/cts_coverage/webglitch_coverage_formatted.json'
cts_coverage_path = '/Users/matthew/Documents/msc/final_proj/cts_coverage/api_coverage_formatted.json'

main(fuzzer_coverage_path, cts_coverage_path)
