import configparser

from Commands.IdentityCommand import IdentityCommand
from Commands.OnyAttunementCommand import OnyAttunementCommand
from Commands.RaidsCommand import RaidsCommand
from Commands.RegisterCommand import RegisterCommand
from Commands.RolesCommand import RolesCommand
from Commands.SheetCommand import SheetCommand

from DataProviders.GoogleCredentialProvider import get_google_credentials
from DataProviders.JorachBotProvider import get_jorach


# Load configuration info
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# Get spreadsheets and worksheets

gc = get_google_credentials()
spreadsheet = gc.open_by_key(config["default"]["SpreadsheetId"])
identity_worksheet = spreadsheet.worksheet("identity")

# Get bot and register commands

bot = get_jorach()
bot.add_cog(IdentityCommand(identity_worksheet=identity_worksheet))
bot.add_cog(OnyAttunementCommand(identity_worksheet=identity_worksheet))
bot.add_cog(RaidsCommand(spreadsheet=spreadsheet, excluded_sheet_names=[identity_worksheet.title]))
bot.add_cog(RegisterCommand(spreadsheet=spreadsheet, identity_worksheet=identity_worksheet))
bot.add_cog(RolesCommand())
bot.add_cog(SheetCommand(spreadsheet_id=spreadsheet.id))


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

print(config["keys"]["DiscordSecret"])
bot.run(config["keys"]["DiscordSecret"])
