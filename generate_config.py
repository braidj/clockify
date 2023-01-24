"""Creates the ini file used by the script"""
import configparser
import logging

logging.basicConfig(level=logging.INFO,filename='set_up.log',filemode='w',
    format='%(asctime)s: %(levelname)s - %(filename)s:%(funcName)s - %(message)s')
config = configparser.ConfigParser()

config['DATA'] = {'hours per day': '8',
                     'client': 'MTC',
                     'data_sheet':'Detailed Report',
                     'debug':'on'}

config['CLOCKIFY COLUMNS'] = {}
report_cols = config['CLOCKIFY COLUMNS']
report_cols['Project'] = 'Project'
report_cols['Description'] = 'Description'
report_cols['User']='User'
report_cols['Start Date']='Date'
report_cols['Duration (decimal)']='Hours'

config.add_section("REPORTING")
config.set("REPORTING","NEW COLUMNS","Milestone,Cost")

config['RATE CARD'] = {}
rate_card = config['RATE CARD']
rate_card['Alex Luketa']=	'81.25'
rate_card['Connor Holloway']=	'62.5'
rate_card['Derek Leung']=	'62.5'
rate_card['Jason Braid']=	'81.25'
rate_card['Jon Willaims']=	'81.25'
rate_card['Matt Gough']=	'62.5'


with open(r"config.ini", 'w',encoding="utf-8") as confFileObject:
    config.write(confFileObject)
    confFileObject.flush()
    confFileObject.close()

print("config.ini created")

read_file = open("config.ini", "r",encoding="utf-8")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()
