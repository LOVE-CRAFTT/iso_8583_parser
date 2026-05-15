"""
CLI tool to parse iso_8583 messages to JSON
including rapid testing on the command line and
batch processing of messages from CSV and .xlsx files.
"""

import sys
import textwrap
import argparse

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
                python cli.py -e excel.xlsx -o completed -> output to completed.json
                '''))


parser.add_argument('-x', '--hex_string', type=str, help='The iso_8583 hex string to be parsed')
parser.add_argument('-c', '--csv', metavar='CSV_FILE', help='csv file or files, space separated')
parser.add_argument('-e', '--excel', metavar='EXCEL_FILE',
                    help='.xlsx file or files, space sparated')

# if option present and no argument then const is used,
# else option and accompanying argument is used
parser.add_argument('-o', '--output', nargs='?', const='output')
parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

args = parser.parse_args()
if len(sys.argv) == 1:
    parser.print_help()

print(args.hex_string, args.csv, args.excel, args.output)
