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
from tabulate import tabulate

import costings
import common_funcs as cf

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)

CLOCKIFY_COLUMNS = [
    'Project', 'PROJECT', 'Description', 'Task', 'User', 'Group', 'Email', 'Tags', 'Billable',
    'Start Date', 'Start Time', 'End Date', 'End Time',
    'Duration (h)', 'Duration (decimal)', 
    'Billable Rate (GBP)', 'Billable Amount (GBP)'
]

#TODO Summarise by distinct Project
#TODO Summarise by distinct Project and Week Nos
#TODO Add Month-Year

cfg = configparser.ConfigParser()
cfg.read('clockify.ini')

sections = cfg.sections()
non_project_sections = ['GLOBAL SETTINGS','CLOCKIFY COLUMNS']
projects = [x for x in sections if x not in non_project_sections]

class HourlyRates:
    """
    Return hourly rates of staff working on a project
    """
    def __init__(self,project,cfg):

        self.project = project
        self.cfg = cfg # config parser object
        self.rate_card_name = self.cfg[project]['rate card']
        self.rates = self.__create_rate_card()
        self.client = self.cfg[project]['client']
        self.type = self.cfg[project]['type']
        self.hpd = self.cfg[project]['hours per day']
        self.missing_users = {}

    def __create_rate_card(self):
        """
        Populates a dictionary with the developer and their hourly rate
        and makes it available
        """
        return costings.all_rates.get(self.rate_card_name,{})
    
    def confirm(self):
        """
        Confirm if all users looked up had a rate defined
        """

        if len(self.missing_users):
            cf.colour_text(f"Missing rates for {list(self.missing_users.keys())}","RED")

        else:
            cf.colour_text("No missing user rates","GREEN")

    def user_rate(self,user):
        """
        Returns the rate for that user
        Main feature
        """

        if user not in self.rates:
            if user not in self.missing_users:
                self.missing_users[user] = 1
            else:
                self.missing_users[user] = self.missing_users[user] + 1

        return self.rates.get(user,0)

    def get_rates(self):
        """
        Return the entire rate card
        Useful for reporting / debugging
        """

        return self.rates

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

    file_type = r'/Clockify*.csv'
    files = glob.glob(search_in +  file_type)
    try:
        max_file = max(files, key=os.path.getctime)
        return max_file
    except ValueError:
        print("There is no recent Clockify report, expecting {file_type}")
        sys.exit(0)

def generate_report(source_date,project,rates):
    """Returns the sorted report data and the file name"""

    cf.colour_text(f"Reporting template used = {rates.project}","GREEN")
    cf.colour_text(f"Hours per day {rates.hpd} for a {rates.type} project using {rates.rate_card_name} rate card","GREEN")
 
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

    # data_frame["Rate"] = data_frame.apply(lambda row: rate_card.rate(row.User), axis=1)
    data_frame["Rate"] = data_frame.apply(lambda row: rates.user_rate(row.User), axis=1)
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
    sort = data_frame.sort_values(["Project","Invoice-Period","Week Number","Date","User"],ascending=True)

    total_cost = sort['Cost'].sum()
    total_hours = sort['Hours'].sum()

    totals_row_df = pd.DataFrame([{
        'Project': 'Total',
        'Description': '',
        'User': '',
        'Date': '',
        'Hours': round(total_hours, 2),
        'Rate': '',
        'Cost': round(total_cost, 2),
        'Week Number': '',
        'Invoice-Period': ''
    }])

    sort = pd.concat([sort, totals_row_df], ignore_index=True)

    sort.to_csv(results_file, index=False)

    return sort,results_file

def main():
    """Main entry point"""

    user_input = input(f"Which project do you want to calculate the cost for ?: {projects}\n")

    if user_input not in projects:
        cf.colour_text(f"Project {user_input} not found","RED")
        sys.exit(0)
    else:
        project = user_input
    rates = HourlyRates(project,cfg)

    user_dir = os.path.expanduser('~')
    download_dir = os.path.join(user_dir, 'Downloads') # search in used specific downloads folder
    source_data = get_clockify_file_name(download_dir)

    data, result_file = generate_report(source_data,project,rates)

    with open(result_file, encoding="utf8") as results_file:
        text = results_file.read()

    pyperclip.copy(text)

    if cfg['GLOBAL SETTINGS']['print'] == 'on':
        cf.colour_text("\nThe following data is available to be pasted from the clipboard\n","GREEN")

        print(tabulate(data, headers=["Project", "Description", "User", "Date","Hours","Rate","Cost","WeekNos","Invoice"], tablefmt="grid"))

    rates.confirm()
    cf.colour_text("Report is now ready to be pasted","GREEN")

if __name__ == "__main__":
    main()
