import configparser

# Method to read config file settings
def read_config():
    """
    How to pull in the config attributes
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config