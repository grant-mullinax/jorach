from discord.ext import commands
import gspread
import configparser
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

config = configparser.ConfigParser()
config.read_file(open('config.ini'))

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    config["keys"]["GoogleCredentialsFile"], scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(config["default"]["SpreadsheetId"])
identity_worksheet = spreadsheet.worksheet("identity")

worksheets = spreadsheet.worksheets()
raid_names = map(lambda ws: ws.title, worksheets)

print(str(list(raid_names)))
