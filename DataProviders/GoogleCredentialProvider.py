import configparser
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# TODO: Should this a singleton-patterned accessible class to make this more robust?

__scope = ["https://spreadsheets.google.com/feeds",
           "https://www.googleapis.com/auth/drive"]

config = configparser.ConfigParser()
config.read_file(open('config.ini'))
__credentials = ServiceAccountCredentials.from_json_keyfile_name(config["keys"]["GoogleCredentialsFile"], __scope)
__gc = gspread.authorize(__credentials)


def get_google_credentials():
    """
    :return: Returns a gspread google credential provider
    """
    return __gc
