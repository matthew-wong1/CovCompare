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
        file_coverage_info = {'percentage': coverage_data['p']}

        # Make a set for the non-covered lines
        non_covered_lines = set()
        raw_non_covered_lines = coverage_data['u']

        for entry in raw_non_covered_lines:
            # index 0: start line
            start_line = entry[0]

            # index 2: end line
            end_line = entry[2]

            # add all numbers between start and end line inclusive to set
            non_covered_lines.update(range(start_line, end_line + 1))

        # Add all the lines numbers (inclusive)
        file_coverage_info['non_covered_lines'] = non_covered_lines
        all_non_covered_lines[file] = file_coverage_info

    return all_non_covered_lines


# def parse_covered_lines(coverage_dict):
#     all_covered_lines = {}
#
#     for file, coverage_data in coverage_dict.items():
#         file_coverage_info = {'percentage': coverage_data['p']}
#         # Make a set for the non-covered lines
#
#         covered_lines = set()
#         raw_covered_lines = coverage_data['g']
#
#         for entry in raw_covered_lines:
#             covered_lines.update(entry['s'])
#
#         file_coverage_info['covered_lines'] = covered_lines
#         all_covered_lines[file] = file_coverage_info
#
#     return all_covered_lines


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


def compare_coverage(fuzzer_non_covered_lines, cts_non_covered_lines):
    coverage_diff = {}

    for file, coverage_data in fuzzer_non_covered_lines.items():
        fuzzer_percent_coverage = coverage_data['percentage']
        file_coverage_info = {'fuzzer_percentage': fuzzer_percent_coverage, 'cts_percentage': cts_non_covered_lines[file]['percentage']}

        lines_not_covered_by_fuzzer = coverage_data['non_covered_lines']
        lines_not_covered_by_cts = cts_non_covered_lines[file]['non_covered_lines']

        lines_covered_by_fuzzer_but_not_cts = lines_not_covered_by_cts.difference(lines_not_covered_by_fuzzer)

        file_coverage_info['lines_missed'] = len(lines_covered_by_fuzzer_but_not_cts)
        coverage_diff[file] = file_coverage_info

    return coverage_diff


def display_difference(difference_in_coverage):
    # Create a list of tuples from the dictionary, selecting both 'percentage' and 'difference' values
    data = [(file, info['fuzzer_percentage'], info['cts_percentage'], info['lines_missed']) for file, info in difference_in_coverage.items()]

    # Create DataFrame with appropriate column names
    df = pd.DataFrame(data, columns=['File', 'Fuzzer coverage (%)', 'CTS coverage (%)', 'Lines missed by CTS'])

    # Sort the DataFrame by the 'File' column
    return df.sort_values(by='File')


# def collate_coverage(dict_to_collate_to, dict_to_collate_from):
#     for file, coverage_data in dict_to_collate_from.items():
#         # Add file to merged dictionary
#         if file not in dict_to_collate_to:
#             dict_to_collate_to[file] = coverage_data
#             continue
#
#         # File present in both dictionaries so need to merge the data
#         percent_coverage_to_merge = coverage_data['percentage']
#         covered_lines_to_merge = coverage_data['covered_lines']
#         num_lines_to_merge = len(covered_lines_to_merge)
#
#         if num_lines_to_merge == 0 or (isinstance(percent_coverage_to_merge, int) and percent_coverage_to_merge == 0):
#             continue
#
#         dict_to_collate_to[file]['covered_lines'].union(covered_lines_to_merge)
#         total_lines = num_lines_to_merge / percent_coverage_to_merge
#         total_covered_lines = len(dict_to_collate_to[file]['covered_lines'])
#         coverage_data['percentage'] = total_covered_lines / total_lines


def cov_compare(fuzzer_cov_path, cts_cov_path):
    # Get coverage stats from JSON
    fuzzer_coverage_dict = load_dict_from_file(fuzzer_cov_path)
    cts_coverage_dict = load_dict_from_file(cts_cov_path)
    cts_shader_coverage_dict = load_dict_from_file(cts_shader_coverage_path)

    # Parse all covered lines by file
    fuzzer_non_covered_lines = parse_non_covered_lines(fuzzer_coverage_dict)
    cts_non_covered_lines = parse_non_covered_lines(cts_coverage_dict)
    cts_shader_non_covered_lines = parse_non_covered_lines(cts_shader_coverage_dict)

    # collate_coverage(cts_non_covered_lines, cts_shader_non_covered_lines)

    # Get a dictionary of the percent covered by fuzzer but not CTS
    difference_in_coverage = compare_coverage(fuzzer_non_covered_lines, cts_non_covered_lines)

    # Print to dataframe
    return display_difference(difference_in_coverage)


# File paths (replace these with the actual paths to your JSON files)
fuzzer_coverage_path = './webglitch_coverage_formatted.json'
cts_coverage_path = './api_coverage_formatted.json'
cts_shader_coverage_path = './cts_shader_coverage.json'

df = cov_compare(fuzzer_coverage_path, cts_coverage_path)
