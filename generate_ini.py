"""Creates the ini file used by the script"""
import configparser
import logging

OUTPUT_FILE='clockify.ini'

logging.basicConfig(level=logging.INFO,filename='set_up.log',filemode='w',
    format='%(asctime)s: %(levelname)s - %(filename)s:%(funcName)s - %(message)s')
config = configparser.ConfigParser()

config['GLOBAL SETTINGS']={
    'data_sheet':'Detailed Report',
    'debug':'on'
}

config['TSP_UK']={
    'client_id': 'Qjc2RDY4OTA4MjNBMTAwQUExNzBDMUE0NEQxQkMwMEU=',
    'client_secret':'Cr0I0quyWm2IBiHg7INzBlUTmNIFKgiqA7keGWVdXWvhMvuVmiEKAdiikxlfyBM93gmC/4h/kWTVSRum6rkhz68jpRuQ9Gq0lRI/7ZJvNTCXS3vKm9D1cWsD4vNvsc/T',
    'AccountName':'signifytechnology',
    'Email Generic':'API@Signify-Tech.com',
    'Email':'jason.braid@xerini.co.uk',
    'Password Generic':'tbc',
    'Password': 'boYLG&m9bGL3KdC'
}

config['TSP_US']={
    'client_id': 'ODYwRjlFOEI4QjM1RDA3RjA2MjlGQTY3QzkzOTY4MUM=',
    'client_secret':'uyOrQn0d7RwqQw9NnCYJziFAMwbZPLjYU3XulRSslxwPpzBQikyYoShv/wchz7RRtw3nX+cs0oyzrpI17eZYaFRgQkf2SAKq23oQJ5ZytKBxhG4/K4dp04qUyms0rUOj',
    'AccountName':'signifytechnologyus',
    'Email':'API@SIgnify-Tech.com'
}


config['MTC'] = {
    'client': 'MTC',
    'hours per day': '8',
    'base rate': '500',
    'higher rate':'620',
    'higher users': "Jason Braid,Alex Luketa"
}

config['VERITHERM'] = {
    'client': 'VERITHERM',
    'hours per day': '7',
    'base rate': '500',
    'higher rate':'500',
    'higher users': "Alex Luketa"
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
