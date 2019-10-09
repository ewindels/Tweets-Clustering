from Scraper import update_all, add_company
from Annotator import Annotator
import argparse
import sys
import pandas as pd

my_parser = argparse.ArgumentParser(description='Launch the Twitter parser')

my_parser.add_argument('--scrap',
                       type=str,
                       help='retrieve tweets from companies or to companies')

my_parser.add_argument('--add',
                       type=str,
                       help='add new company')

my_parser.add_argument('--annot',
                       type=str,
                       help='add new company')

args = my_parser.parse_args()

scrap = args.scrap
new_company = args.add
annot_company = args.annot

if scrap:
    if scrap not in ['from', 'to']:
        print("The mode specified does not exist (only 'to' and 'from' are supported)")
        sys.exit()
    else:
        update_all(scrap)

if new_company:
    add_company(new_company)
    df_single = pd.DataFrame(columns=['tweet_id', 'category', 'toxicity', 'intent'])
    df_comp = pd.DataFrame(columns=['tweet_id_1', 'tweet_id_2', 'similarity'])

    df_single.to_csv('annotations/{}_single.csv'.format(new_company), index=False)
    df_comp.to_csv('annotations/{}_comp.csv'.format(new_company), index=False)

if annot_company:
    annotator = Annotator(annot_company)
    mode = int(input("Single (1) or Comparison (2)?"))
    if mode == 1:
        annotator.annotate('single')
    elif mode == 2:
        annotator.annotate('comp')

