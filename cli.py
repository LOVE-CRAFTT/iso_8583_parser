"""
CLI tool to parse iso_8583 messages to JSON
including rapid testing on the command line and
batch processing of messages from CSV and .xlsx files.
"""

import sys
import textwrap
import argparse
import csv
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from iso8583 import iso_8583_to_json

parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    allow_abbrev = False,
    description = textwrap.dedent('''
                cli.py parses iso_8583 hex strings to JSON.
                It also parses hex values present in .csv or .xlsx files
                    in such cases, one hex string is expected per line.
                Output is to stdout/terminal by default,
                    output.json if -o wih no argument and [argument].json if an argument is provided
                                  
                NOTE: It's not recommended to output vaues parsed from csv or excel files to output as
                      there might be a lot of them.
                
                example:
                python cli.py -x "30 32 30 30 F2 38 44 80 20 C0 80 00 00 00 00 00 ..." -> outputs to terminal
                python cli.py --csv file1.csv -o -> outputs to output.json
                python cli.py -e excel.xlsx -o completed -> outputs to completed.json
                '''))


parser.add_argument('-x', '--hex_string', type=str, help='The iso_8583 hex string to be parsed')
parser.add_argument('-c', '--csv', metavar='CSV_FILE', help='csv file or files, space separated')
parser.add_argument('-e', '--excel', metavar='EXCEL_FILE',
                    help='.xlsx file or files, space separated')

# if option present and no argument then const is used,
# else option and accompanying argument is used
parser.add_argument('-o', '--output', nargs='?', const='output')
parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

class InputTypeEnum(Enum):
    """
    Enum representing valid input types
    """
    CSV = 1
    EXCEL = 2
    HEXADECIMAL_STRING = 3

@dataclass
class ParsedArgs:
    """
    Convenience class to move parsed cli arguments around
    """
    input_value: str
    input_type: InputTypeEnum
    output: str

def get_arguments() -> ParsedArgs | None:
    """
    Function to get values passed to the cli tool, if the values are valid.
    """
    args = parser.parse_args()

    # sys.argv equals 1 only if there are no arguments, it's reasonable to then show the help
    if len(sys.argv) == 1:
        parser.print_help()
        return None

    options = []
    if args.hex_string is not None:
        options.append((args.hex_string, InputTypeEnum.HEXADECIMAL_STRING))
    if args.csv is not None:
        options.append((args.csv, InputTypeEnum.CSV))
    if args.excel is not None:
        options.append((args.excel, InputTypeEnum.EXCEL))

    # if no input was provided
    if not options:
        print('[INCORRECT-USAGE]: no input arguments')
        parser.print_usage()
        return None

    # more than one input type
    if len(options) > 1:
        print('[INCORRECT-USAGE]: too many input arguments')
        parser.print_usage()
        return None

    input_value, input_type = options[0]
    return ParsedArgs(input_value=input_value, input_type=input_type, output=args.output)

def preprocess_source_and_dest_files(input_file_name, output_file_name, input_file_type):
    """empty"""
    first_pass_through = True
    while not output_file_name:
        if first_pass_through:
            print(textwrap.dedent("""
                  It's not recommended to output vaues parsed from csv or excel files to output
                  as there might be a lot of them!!!"""))
        response = input("Output to file instead? (y/n): ")
        if response.lower() == 'n':
            break
        if response.lower() == 'y':
            output_file_name = input("\nEnter file name: ")
        else:
            print("\nInvalid response, try again\n")
            first_pass_through = False

    input_path = Path(input_file_name)
    if not input_path.suffix or input_path.suffix == '.':
        print('ERROR: Please include the full filename with file extension (.csv or .xlsx).')
        sys.exit(-1)

    if input_file_type == InputTypeEnum.CSV:
        if input_path.suffix != '.csv':
            print('Error: Input file must have a .csv extension')
            sys.exit(-1)
    elif input_file_type == InputTypeEnum.EXCEL:
        if input_path.suffix != '.xlsx':
            print('Error: Input file must have a .xlsx extension')
            sys.exit(-1)

    if not input_path.exists():
        print(f"ERROR: File '{input_file_name} could not be found")
        sys.exit(-1)

    # attempt to open files
    with open(input_file_name) as csv_file:
        r = csv.reader(csv_file)
        for row in r:
            print(row)




def parse_hex(hex_string, output_file_name):
    """
    Parse iso_8583 hex strings
    """
    parsed_json_string = iso_8583_to_json(hex_string)
    if output_file_name is None:
        print('\n\n=======================================================================')
        print(parsed_json_string)
    else:
        #TODO: replace with just the output_file_name.json
        p = 'random' / Path(output_file_name + '.json')
        p.write_text(parsed_json_string)


def parse_csv(csv_file_name, output_file_name):
    """
    Parse iso_8583 hex string in csv files
    """
    preprocess_source_and_dest_files(csv_file_name, output_file_name, InputTypeEnum.CSV)

def parse_excel(excel_file_name, output_file_name): #pylint: disable=unused-argument
    """
    Parse iso_8583 hex strings in excel files
    """
    preprocess_source_and_dest_files(excel_file_name, output_file_name, InputTypeEnum.EXCEL)


if __name__ == '__main__':
    # end program if there's nothing to work on
    arguments = get_arguments()
    if arguments is None:
        sys.exit(-1)

    if arguments.input_type == InputTypeEnum.HEXADECIMAL_STRING:
        parse_hex(arguments.input_value, arguments.output)
    elif arguments.input_type == InputTypeEnum.CSV:
        parse_csv(arguments.input_value, arguments.output)
    elif arguments.input_type == InputTypeEnum.EXCEL:
        parse_excel(arguments.input_value, arguments.output)
