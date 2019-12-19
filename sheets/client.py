import configparser
from gspread.client import Client

import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials


class RetryClient(Client):
    def request(self, method, endpoint, params=None, data=None, json=None, files=None, headers=None):
        response = getattr(self.session, method)(
            endpoint,
            json=json,
            params=params,
            data=data,
            files=files,
            headers=headers
        )

        if not response.ok:
            if response.status_code == 401:
                self.login()
                response = getattr(self.session, method)(
                    endpoint,
                    json=json,
                    params=params,
                    data=data,
                    files=files,
                    headers=headers
                )
                if not response.ok:
                    raise APIError(response)
            else:
                raise APIError(response)

        return response


def get_spreadsheet_link():
    return "https://docs.google.com/spreadsheets/d/{}".format(spreadsheet_id)


def add_worksheet(**kwargs):
    return spreadsheet.add_worksheet(**kwargs)


def get_worksheet(worksheet_key):
    return spreadsheet.worksheet(worksheet_key)


def get_worksheets():
    return spreadsheet.worksheets()


def get_raid_worksheets():
    return [sheet for sheet in get_worksheets() if sheet.title not in _excluded_sheet_names]


def get_identity_worksheet():
    return identity_worksheet


def delete_row(worksheet, index):
    worksheet.delete_row(index)


def duplicate_sheet(new_sheet_name):
    return get_worksheet("template").duplicate(new_sheet_name=new_sheet_name)


def append_row(worksheet, contents: list):
    worksheet.append_row(contents)


def insert_row(worksheet, contents: list, index):
    worksheet.insert_row(contents, index)


def col_values(worksheet, index):
    return worksheet.col_values(index)


def row_values(worksheet, index):
    return worksheet.row_values(index)


def update_cell(worksheet, row_index, col_index, value):
    return worksheet.update_cell(row_index, col_index, value)


def get_worksheet_link(worksheet):
    return "{}#gid={}".format(get_spreadsheet_link(), worksheet.id)


def get_rows_with_value_in_column(worksheet, column_index, value_to_find, list_search_rows=None):
    """
    Returns a list of rows where the specified value is found in the input column.

    By default, this searches through all rows.
    If specific rows should be iterated through, they can be input via `list_search_rows`.

    :param worksheet: The worksheet to search through
    :param column_index: The column to search for the input value in
    :param value_to_find: The value that should be found
    :param list_search_rows: Optional: The 1-indexed list of rows that should be searched through.
    :return: A list of rows where the value was found in the specific column.
    """
    cols_of_values = col_values(worksheet, column_index)

    if list_search_rows:
        # Filter; search each individual valid row
        valid_rows = [row for row in list_search_rows if row - 1 < len(cols_of_values)]
        return [row for row in valid_rows if cols_of_values[row - 1] == value_to_find]
    else:
        # No filter
        # Get all rows with the specified value; +1 as gsheets is 1-indexed
        return [index + 1 for index, value in enumerate(cols_of_values) if value == value_to_find]


_excluded_sheet_names = ["identity", "template"]

__scope = ["https://spreadsheets.google.com/feeds",
           "https://www.googleapis.com/auth/drive"]

__config = configparser.ConfigParser()
__config.read_file(open('config.ini'))
__credentials = ServiceAccountCredentials.from_json_keyfile_name(__config["keys"]["GoogleCredentialsFile"], __scope)
spreadsheet_id = __config["default"]["SpreadsheetId"]
gc = gspread.authorize(__credentials, client_class=RetryClient)
gc.login()

spreadsheet = gc.open_by_key(spreadsheet_id)
identity_worksheet = get_worksheet("identity")
