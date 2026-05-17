"""
CLI tool to parse iso_8583 messages to JSON
including rapid testing on the command line and
batch processing of messages from CSV and .xlsx files.
"""

import sys
import textwrap
import argparse
from enum import Enum
from dataclasses import dataclass

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


def parse_hex(hex_string):
    """
    Parse iso_8583 hex strings
    """
    print('\n\n ========================================================================')
    print(iso_8583_to_json(hex_string))

def parse_csv(csv_file): #pylint: disable=unused-argument
    """
    Parse iso_8583 hex string in csv files
    """

def parse_excel(excel_file): #pylint: disable=unused-argument
    """
    Parse iso_8583 hex strings in excel files
    """


if __name__ == '__main__':
    # end program if there's nothing to work on
    arguments = get_arguments()
    if arguments is None:
        sys.exit(-1)

    if arguments.input_type == InputTypeEnum.HEXADECIMAL_STRING:
        parse_hex(arguments.input_value)
    elif arguments.input_type == InputTypeEnum.CSV:
        parse_csv(arguments.input_type)
    elif arguments.input_type == InputTypeEnum.EXCEL:
        parse_excel(arguments.input_type)
