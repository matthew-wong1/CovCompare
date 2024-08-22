import json, sys
import pandas as pd

def load_dict_from_file(file_path):
    """ Load JSON dictionary from a file. """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)['f']
    except FileNotFoundError:
        print("File not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        sys.exit(1)

def parse_non_covered_lines(coverage_dict):
    all_non_covered_lines = {}

    for file, coverage_data in coverage_dict.items():
        # Parse percentage
        file_coverage_info = {}

        file_coverage_info['percentage'] = coverage_data['p']

        # Make a set for the non-covered lines
        non_covered_lines = set()
        raw_uncovered_lines = coverage_data['u']

        for entry in raw_uncovered_lines:
            # index 0: start line
            start_line = entry[0]

            # index 2: end line
            end_line = entry[2]

            # add all numbers between start and end line inclusive to set
            non_covered_lines.update(range(start_line, end_line + 1))

        # Add all the lines numbers (inclusive)
        file_coverage_info['uncovered_lines'] = non_covered_lines
        all_non_covered_lines[file] = file_coverage_info

    return all_non_covered_lines


def parse_covered_lines(coverage_dict):
    all_covered_lines = {}

    for file, coverage_data in coverage_dict.items():
        file_coverage_info = {'percentage': coverage_data['p']}
        # Make a set for the non-covered lines

        covered_lines = set()
        raw_covered_lines = coverage_data['g']

        for entry in raw_covered_lines:
            covered_lines.update(entry['s'])

        file_coverage_info['covered_lines'] = covered_lines
        all_covered_lines[file] = file_coverage_info

    return all_covered_lines

# def compare_coverage(fuzzer_non_covered_lines, cts_non_covered_lines):
#     coverage_diff = {}
#     for file, coverage in fuzzer_non_covered_lines.items():
#         lines_not_covered_by_fuzzer = fuzzer_non_covered_lines[file]['uncovered_lines']
#
#         if (file in cts_non_covered_lines):
#             lines_not_covered_by_cts = cts_non_covered_lines[file]['uncovered_lines']
#         else:
#             lines_not_covered_by_cts = set()
#
#         lines_covered_by_fuzzer_and_not_cts = lines_not_covered_by_cts.difference(lines_not_covered_by_fuzzer)
#
#     return coverage_diff


def compare_coverage(fuzzer_covered_lines, cts_covered_lines):
    coverage_diff = {}
    for file, coverage_data in fuzzer_covered_lines.items():
        fuzzer_percent_coverage = fuzzer_covered_lines[file]['percentage']
        lines_covered_by_fuzzer = fuzzer_covered_lines[file]['covered_lines']

        if (file in cts_covered_lines):
            lines_covered_by_cts = cts_covered_lines[file]['covered_lines']
            cts_percent_coverage = cts_covered_lines[file]['percentage']
        else:
            lines_covered_by_cts = set()
            cts_percent_coverage = 0

        # because it is offset for some reason
        modified_lines_covered_by_fuzzer = { line_num - 336 for line_num in lines_covered_by_fuzzer}
        lines_covered_by_fuzzer_and_not_cts = modified_lines_covered_by_fuzzer.difference(lines_covered_by_cts)
        num_lines_covered_by_fuzzer_and_not_cts = len(lines_covered_by_fuzzer_and_not_cts)

        if int(fuzzer_percent_coverage) == 0:
            coverage_diff[file] = 0
            continue
        print(fuzzer_covered_lines[file])

        if (cts_percent_coverage == 0):
            total_lines = len(lines_covered_by_fuzzer) / fuzzer_percent_coverage
        else:
            total_lines = len(lines_covered_by_cts) / cts_percent_coverage

        if num_lines_covered_by_fuzzer_and_not_cts == 0:
            coverage_diff[file] = 0
        else:
            coverage_diff[file] = 100 * num_lines_covered_by_fuzzer_and_not_cts / total_lines

    return coverage_diff


def display_difference(difference_in_coverage):
    df = pd.DataFrame(list(difference_in_coverage.items()), columns=['File', 'Coverage Percentage'])
    sorted_df = df.sort_values(by='File', ascending=False)
    print(sorted_df)


def main(fuzzer_coverage_path, cts_coverage_path):
    # Get coverage stats from JSON
    fuzzer_coverage_dict = load_dict_from_file(fuzzer_coverage_path)
    cts_coverage_dict = load_dict_from_file(cts_coverage_path)

    # Parse all covered lines by file
    fuzzer_covered_lines = parse_covered_lines(fuzzer_coverage_dict)
    cts_covered_lines = parse_covered_lines(cts_coverage_dict)

    # Get a dictionary of the percent covered by fuzzer but not CTS
    difference_in_coverage = compare_coverage(fuzzer_covered_lines, cts_covered_lines)

    # Print to dataframe
    display_difference(difference_in_coverage)


# File paths (replace these with the actual paths to your JSON files)
fuzzer_coverage_path = './webglitch_coverage_formatted.json'
cts_coverage_path = './api_coverage_formatted.json'

main(fuzzer_coverage_path, cts_coverage_path)
