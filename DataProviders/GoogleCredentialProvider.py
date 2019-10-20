import configparser
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# TODO: Should this a singleton-patterned accessible class to make this more robust?

__scope = ["https://spreadsheets.google.com/feeds",
           "https://www.googleapis.com/auth/drive"]

__config = configparser.ConfigParser()
__config.read_file(open('config.ini'))
__credentials = ServiceAccountCredentials.from_json_keyfile_name(__config["keys"]["GoogleCredentialsFile"], __scope)
__gc = gspread.authorize(__credentials)


def get_google_credentials():
    """
    :return: Returns a gspread google credential provider
    """
    return __gc
