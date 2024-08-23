import zlib

def decompress_and_format_lcov(input_path, output_path):
    with open(input_path, 'rb') as f:
        compressed_data = f.read()
        decompressed_data = zlib.decompress(compressed_data, zlib.MAX_WBITS|32).decode('utf-8')

    # Assuming the standard lcov format where each new record starts with 'SF:' or 'TN:'
    # and 'end_of_record' is the end of a block, we insert newlines appropriately.
    formatted_data = decompressed_data.replace('end_of_record', 'end_of_record\n')
    formatted_data = formatted_data.replace('SF:', '\nSF:')

    with open(output_path, 'w') as f:
        f.write(formatted_data)

# Specify the path to the compressed file and the path for the decompressed and formatted output
input_path = '/Users/matthew/Documents/msc/final_proj/cts_coverage/webglitch_coverage_llvm.lcov'
output_path = '/Users/matthew/Documents/msc/final_proj/cts_coverage/webglitch_coverage_llvm_formatted.json'

decompress_and_format_lcov(input_path, output_path)

