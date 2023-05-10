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
import warnings
import pyperclip
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)

CLOCKIFY_COLUMNS = [
    'Project', 'PROJECT', 'Description', 'Task',
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

def format_date(data_frame,column):
    """Convert a string date column to a specific format"""
    data_frame[column] = pd.to_datetime(data_frame.Date,format='%d/%m/%Y')
    data_frame[column] = data_frame[column].dt.strftime('%d/%m/%Y')
    return data_frame

def remove_carriage_returns(data_frame, column):
    """Removes carraige returns"""
    data_frame[column] = data_frame[column].str.replace('\n', '.')
    return data_frame

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

    rate = float(cfg[template][rate]) / float(cfg[template]["hours per day"])
    return round(rate,2)

def get_higher_rate_user(template):
    """
    Returns a list of user who are charged at the higher rate
    """
    result = cfg[template]['higher users']
    return result.split(',')

def generate_report(source_date,project):
    """Returns the sorted report data and the file name"""

    base_day_rate = calc_rate(project,"base rate")
    higher_hourly_rate = calc_rate(project,"higher rate")
    higher_rate_users = get_higher_rate_user(project)
    hours_per_day = cfg[project]['hours per day']

    rate_card = RateCard(higher_rate_users,higher_hourly_rate,base_day_rate)

    print(f"Reporting template used = {project}")
    print(f"Hours per day {hours_per_day} at a base rate of {base_day_rate}")
    print(f"Higher hourly rate = {higher_hourly_rate} for {higher_rate_users}")

    required_columns = list(cfg['CLOCKIFY COLUMNS'].keys())
    adjusted_names = list(cfg['CLOCKIFY COLUMNS'].values())
    results_file = cfg['GLOBAL SETTINGS']['results']

    with warnings.catch_warnings(record=True): # hide a useless warning fromm pd
        warnings.simplefilter("always")
        data_frame  = pd.read_csv(source_date)

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

    if cfg.has_option(project, 'custom column'):
        new_col_name = cfg.get(project, 'custom column')
        data_frame[new_col_name] = "Not set"

    data_frame = remove_carriage_returns(data_frame,"Description")
    data_frame = remove_carriage_returns(data_frame,"Project")

    # sort = data_frame.sort_values("Week Number", axis=0, ascending=False,
    # inplace=False, kind='quicksort', na_position='last')
    sort = data_frame.sort_values(["Invoice-Period","Week Number","Date","User"],ascending=True)

    sort.to_csv(results_file, index=False)

    return sort,results_file

def main():
    """Main entry point"""
    #TODO handle if no recent csv file
    #TODO Refactor so main just contains which PROJECT to run for

    project = "MTC"

    user_dir = os.path.expanduser('~')
    download_dir = os.path.join(user_dir, 'Downloads') # search in used specific downloads folder
    source_data = get_clockify_file_name(download_dir)

    data, result_file = generate_report(source_data,project)

    with open(result_file, encoding="utf8") as results_file:
        text = results_file.read()

    pyperclip.copy(text)

    if cfg['GLOBAL SETTINGS']['print'] == 'on':
        print("\nThe following data is available to be pasted from the clipboard\n")
        print(data)

    print("Report is now ready to be pasted")

if __name__ == "__main__":
    main()
