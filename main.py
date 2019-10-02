from Scraper import update_all, add_company
import argparse
import sys

my_parser = argparse.ArgumentParser(description='Launch the Twitter parser')

my_parser.add_argument('--mode',
                       type=str,
                       help='retrieve tweets from companies or to companies')

my_parser.add_argument('--add',
                       type=str,
                       help='add new company')

args = my_parser.parse_args()
input_mode = args.mode
new_company = args.add

if input_mode:
    if input_mode not in ['from', 'to']:
        print("The mode specified does not exist (only 'to' and 'from' are supported)")
        sys.exit()
    else:
        update_all(input_mode)
if new_company:
    add_company(new_company)
