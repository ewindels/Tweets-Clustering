from Scraper import update_all
import argparse
import sys

my_parser = argparse.ArgumentParser(description='Launch the Twitter parser')

my_parser.add_argument('--mode',
                       type=str,
                       help='retrieve tweets from companies or to companies')

args = my_parser.parse_args()
input_mode = args.mode

if input_mode not in ['from', 'to']:
    print("The mode specified does not exist (only 'to' and 'from' are supported)")
    sys.exit()

update_all(input_mode)
