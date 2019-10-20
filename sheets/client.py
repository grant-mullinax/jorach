import configparser
from functools import wraps

import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials


identity_worksheet = None

def retry(tries=2):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        tries: Number of times to try (not retry) before giving up.
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries = tries
            while mtries >= 1:
                try:
                    return f(*args, **kwargs)
                except APIError as e:
                    mtries -= 1
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def get_spreadsheet_link():
        return "https://docs.google.com/spreadsheets/d/{}".format(spreadsheet_id)

@retry()
def add_worksheet(**kwargs):
    return spreadsheet.add_worksheet(**kwargs)

@retry()
def get_worksheet(worksheet_key):
    return spreadsheet.worksheet(worksheet_key)

@retry()
def get_worksheets():
    return spreadsheet.worksheets()

@retry()
def get_identity_worksheet():
    if identity_worksheet == None:
        return spreadsheet.worksheet("identity")
    return identity_worksheet

@retry()
def delete_row(worksheet, index):
    worksheet.delete_row(index)

@retry()
def duplicate_sheet(new_sheet_name):
    return get_worksheet("template").duplicate(new_sheet_name=new_sheet_name)

@retry()
def append_row(worksheet, contents: list):
    worksheet.append_row(contents)

@retry()
def insert_row(worksheet, contents: list, index):
    worksheet.insert_row(contents, index)

@retry()
def col_values(worksheet, index):
    return worksheet.col_values(index)

@retry()
def row_values(worksheet, index):
    return worksheet.row_values(index)

@retry()
def update_cell(worksheet, row_index, col_index, value):
    return worksheet.update_cell(row_index, col_index, value)


__scope = ["https://spreadsheets.google.com/feeds",
           "https://www.googleapis.com/auth/drive"]

__config = configparser.ConfigParser()
__config.read_file(open('config.ini'))
__credentials = ServiceAccountCredentials.from_json_keyfile_name(__config["keys"]["GoogleCredentialsFile"], __scope)
spreadsheet_id = __config["default"]["SpreadsheetId"]
gc = gspread.authorize(__credentials)
gc.login()
spreadsheet = gc.open_by_key(spreadsheet_id)
identity_worksheet = get_identity_worksheet()
