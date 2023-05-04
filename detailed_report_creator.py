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
import warnings

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)

CLOCKIFY_COLUMNS = [
    'Project', 'Client', 'Description', 'Task',
    'User', 'Group', 'Email', 'Tags', 'Billable',
    'Start Date', 'Start Time', 'End Date', 'End Time',
    'Duration (h)', 'Duration (decimal)', 
    'Billable Rate (GBP)', 'Billable Amount (GBP)']

#TODO Summarise by distinct Project
#TODO Summarise by distinct Project and Week Nos
#TODO Add Month-Year

cfg = configparser.ConfigParser()

cfg.read('clockify.ini')

class RateCard:
    """
    Store the higher rate users hourly rates
    """
    def __init__(self,higher_rate_users,higher_rate,base_rate) -> None:
        self.directors = higher_rate_users
        self.director_rate = higher_rate
        self.base_rate = base_rate

    def rate(self,user):
        """
        Returns the appropriate rate for that user
        """

        if user in self.directors:
            return self.director_rate

        return self.base_rate

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
    df[column] = df[column].str.replace('\n', '.')
    return df

def get_clockify_file_name(search_in):
    """Returns the name of the last file in search folder that starts with Clockify_"""

    file_type = r'/Clockify_*.csv'
    files = glob.glob(search_in +  file_type)
    try:
        max_file = max(files, key=os.path.getctime)
        return max_file
    except ValueError:
        print("There is no recent Clockify report")
        sys.exit(0)

def calc_rate(template, rate):
    """
    Returns the rate to 2 dec places
    """

    rate = float(cfg[template]["base rate"]) / float(cfg[template]["hours per day"])
    return round(rate,2)

def get_higher_rate_user(template):
    """
    Returns a list of user who are charged at the higher rate
    """
    result = cfg[template]['higher users']
    return result.split(',')

def main():
    """Main entry point"""
    #TODO handle if no recent csv file
    #TDOO Refactor so main just contains which client to run for
    CLIENT = "SIGNIFY"
    HOUR_BASE_RATE = calc_rate(CLIENT,"base rate")
    HOUR_DIRECTOR_RATE = calc_rate(CLIENT,"higher rate")
    HIGHER_RATE_USERS = get_higher_rate_user(CLIENT)

    rate_card = RateCard(HIGHER_RATE_USERS,HOUR_DIRECTOR_RATE,HOUR_BASE_RATE)

    print(f"Base hourly rate = {HOUR_BASE_RATE}")
    print(f"Higher hourly rate = {HOUR_DIRECTOR_RATE}")
    print(f"Higher rate users = {HIGHER_RATE_USERS}")
    print(f"Reporting template used = {CLIENT}")

    user_dir = os.path.expanduser('~')
    download_dir = os.path.join(user_dir, 'Downloads') # search in used specific downloads folder
    data_sheet = cfg['GLOBAL SETTINGS']['data_sheet']

    required_columns = list(cfg['CLOCKIFY COLUMNS'].keys())
    adjusted_names = list(cfg['CLOCKIFY COLUMNS'].values())

    report_csv = get_clockify_file_name(download_dir)

    with warnings.catch_warnings(record=True): # hide a useless warning fromm pd
        warnings.simplefilter("always")
        data_frame  = pd.read_csv(report_csv)

    data_frame.rename(columns=str.lower, inplace=True)

    data_frame = data_frame[required_columns]  # just these columns
    data_frame.columns = adjusted_names  # rename them
    data_frame.is_copy = False
    data_frame["Hours"] = data_frame["Hours"].astype(float)

    data_frame["Rate"] = data_frame.apply(lambda row: rate_card.rate(row.User), axis=1)

    data_frame["Rate"] = data_frame["Rate"].astype(float)
    data_frame=format_date(data_frame,"Date")

    data_frame["Cost"] = data_frame['Rate'] * data_frame['Hours']
    data_frame["Week Number"] = data_frame["Date"].apply(week_number)

    data_frame["Invoice-Period"] = data_frame["Date"].apply(invoice_period)
    data_frame["Milestone"] = "Not set"

    data_frame = remove_carriage_returns(data_frame,"Description")
    data_frame = remove_carriage_returns(data_frame,"Project")

    # sort = data_frame.sort_values("Week Number", axis=0, ascending=False,
    # inplace=False, kind='quicksort', na_position='last')
    sort = data_frame.sort_values(["Invoice-Period","Week Number","Date","User"],ascending=True)

    sort.to_csv("results.csv", index=False)

    with open("results.csv", encoding="utf8") as results_file:
        text = results_file.read()

    pyperclip.copy(text)

    if cfg['GLOBAL SETTINGS']['debug'] == 'on':
        print("\nThe following data is available to be pasted from the clipboard\n")
        print(sort)

    print("Report is now ready to be pasted")


if __name__ == "__main__":
    main()
