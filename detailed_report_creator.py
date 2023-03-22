"""
Utility to format clockify report easily
Usage: download clockify report as xlsx, run script,
paste contents from clipboard
"""
import os
from datetime import datetime
import sys
import configparser
import glob
import pandas as pd
import pyperclip

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)

#TODO Summarise by distinct Project
#TODO Summarise by distinct Project and Week Nos
#TODO Add Month-Year

cfg = configparser.ConfigParser()
cfg.read('config.ini')

def invoice_period(date_string):
    """To help with invoicing display the date as mm-yyyy"""
    original = datetime.strptime(date_string, '%d/%m/%Y')
    shorter = original.strftime('%Y-%m')
    return f"INV-{shorter}"

def week_number(date_string):
    """Get week number, avoid bug in pf"""
    date = datetime.strptime(date_string, '%d/%m/%Y')
    return date.isocalendar()[1]

def format_date(df,column):
    """Convert a string date column to a specific format"""
    df[column] = pd.to_datetime(df.Date,format='%d/%m/%Y')
    df[column] = df[column].dt.strftime('%d/%m/%Y')
    return df

def remove_carriage_returns(df, column):
    """Removes carraige returns"""
    df[column] = df[column].str.replace('\n\r', '')
    df[column] = df[column].str.replace('\n', '')
    return df

def get_clockify_file_name(search_in):
    """Returns the name of the last file in search folder that starts with Clockify_"""

    file_type = r'/Clockify_*.xlsx'
    files = glob.glob(search_in +  file_type)
    try:
        max_file = max(files, key=os.path.getctime)
        return max_file
    except ValueError:
        print("There is no recent Clockify report")
        sys.exit(0)

def main():
    """Main entry point"""
    user_dir = os.path.expanduser('~')
    download_dir = os.path.join(user_dir, 'Downloads')
    data_sheet = cfg['DATA']['data_sheet']

    required_columns = list(cfg['CLOCKIFY COLUMNS'].keys())
    adjusted_names = list(cfg['CLOCKIFY COLUMNS'].values())

    report_xlsx = get_clockify_file_name(download_dir)

    data_frame = pd.read_excel(report_xlsx,
                       sheet_name=data_sheet, dtype=str)

    data_frame.rename(columns=str.lower, inplace=True)
    data_frame = data_frame[required_columns]  # just these columns
    data_frame.columns = adjusted_names  # rename them
    data_frame.is_copy = False
    data_frame["Hours"] = data_frame["Hours"].astype(float)

    data_frame["Rate"] = data_frame.apply(lambda row: cfg.get(
        "RATE CARD", row.User, fallback=0), axis=1)

    data_frame["Rate"] = data_frame["Rate"].astype(float)
    data_frame=format_date(data_frame,"Date")

    data_frame["Cost"] = data_frame['Rate'] * data_frame['Hours']
    data_frame["Week Number"] = data_frame["Date"].apply(week_number)
    
    data_frame["Invoice-Period"] = data_frame["Date"].apply(invoice_period)
    data_frame["Milestone"] = "Not set"

    data_frame = remove_carriage_returns(data_frame,"Description")
    data_frame = remove_carriage_returns(data_frame,"Project")

    sort = data_frame.sort_values("Week Number", axis=0, ascending=False,
    inplace=False, kind='quicksort', na_position='last')

    sort.to_csv("results.csv", index=False)

    with open("results.csv", encoding="utf8") as results_file:
        text = results_file.read()

    pyperclip.copy(text)

    if cfg['DATA']['debug'] == 'on':
        print("\nThe following data is available to be pasted from the clipboard\n")
        print(sort)

    print("Report is now ready to be pasted")


if __name__ == "__main__":
    main()
