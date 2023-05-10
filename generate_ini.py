"""Creates the ini file used by the script"""
import configparser
import logging

OUTPUT_FILE='clockify.ini'

logging.basicConfig(level=logging.INFO,filename='set_up.log',filemode='w',
    format='%(asctime)s: %(levelname)s - %(filename)s:%(funcName)s - %(message)s')
config = configparser.ConfigParser()

config['GLOBAL SETTINGS']={
    'data_sheet':'Detailed Report',
    'print':'on',
    'results': 'results.csv'
}

config['MTC'] = {
    'client': 'MTC',
    'hours per day': '8',
    'base rate': '500',
    'higher rate':'620',
    'higher users': "Jason Braid,Alex Luketa",
    'custom column': 'milestone'
}

config['VERITHERM'] = {
    'client': 'VERITHERM',
    'hours per day': '7',
    'base rate': '500',
    'higher rate':'500',
    'higher users': "Alex Luketa"
}

config['SMART HTC'] = {
    'client': 'VERITHERM',
    'hours per day': '7',
    'base rate': '437.50',
    'higher rate':'437.50',
    'higher users': "Alex Luketa,Jason Braid"
}


config['500_BY_8'] = {
    'client': 'GENERIC',
    'hours per day': '8',
    'base rate': '500',
    'higher rate':'500',
    'higher users': "Alex Luketa,Simon Burgess,Jon Williams"
}

config['500_BY_7'] = {
    'client': 'GENERIC',
    'hours per day': '7',
    'base rate': '500',
    'higher rate':'500',
    'higher users': "Alex Luketa,Simon Burgess,Jon Williams"
}

config['SIGNIFY'] = {
    'client': 'SIGNIFY',
    'hours per day': '7',
    'base rate': '420',
    'higher rate':'420',
    'higher users': "Alex Luketa,Simon Burgess,Jon Williams"
}

# Global
config['CLOCKIFY COLUMNS'] = {}
report_cols = config['CLOCKIFY COLUMNS']
report_cols['Project'] = 'Project'
report_cols['Description'] = 'Description'
report_cols['User']='User'
report_cols['Start Date']='Date'
report_cols['Duration (decimal)']='Hours'

config.add_section("REPORTING")
config.set("REPORTING","NEW COLUMNS","Milestone,Cost")

with open(OUTPUT_FILE, 'w',encoding="utf-8") as confFileObject:
    config.write(confFileObject)
    confFileObject.flush()
    confFileObject.close()

print(f"{OUTPUT_FILE} created")

read_file = open(OUTPUT_FILE, "r",encoding="utf-8")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()
