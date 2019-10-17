from discord.ext import commands
import gspread
import configparser
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

config = configparser.ConfigParser()
config.read_file(open('config.ini'))

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name(config["keys"]["GoogleCredentialsFile"], scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(config["default"]["SpreadsheetId"])
identity_worksheet = spreadsheet.worksheet("identity")

bot = commands.Bot(command_prefix="!", description="its jorach")

wow_classes = ["druid", "hunter", "mage", "paladin", "priest", "rogue", "warlock", "warrior"]
roles = ["dps", "tank", "healer"]


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.command()
async def identity(ctx, name: str, wow_class: str, role: str):
    if wow_class.lower() not in wow_classes:
        await ctx.send("invalid class name")
        return

    if role.lower() not in roles:
        await ctx.send("invalid role, valid roles are " + str(roles))
        return

    discord_ids = identity_worksheet.col_values(1)
    author_hash = str(hash(ctx.author))

    if author_hash in discord_ids:
        identity_worksheet.delete_row(discord_ids.index(author_hash) + 1)  # sheets is indexed starting at 1

    identity_worksheet.append_row([author_hash, str(ctx.author), name, wow_class, role])
    await ctx.send("your identity has been saved")


@bot.command()
async def register(ctx, raid_name: str):
    raid_name_lower = raid_name.lower()

    if raid_name_lower == "identity":
        await ctx.send("nice try")
        return

    discord_ids = identity_worksheet.col_values(1)
    author_hash = str(hash(ctx.author))

    if author_hash not in discord_ids:
        await ctx.send("your identity has not been saved! please use the !identity command")
        return

    worksheets = spreadsheet.worksheets()
    raid_names = map(lambda ws: ws.title, worksheets)
    if raid_name_lower not in raid_names:
        await ctx.send("that is not a valid raid! valid raids are: " + str(raid_names))
        return

    raid_worksheet = spreadsheet.worksheet(raid_name_lower)
    identity_values = identity_worksheet.row_values(discord_ids.index(author_hash) + 1)

    name, wow_class, role = (identity_values[2], identity_values[3], identity_values[4])
    names = raid_worksheet.col_values(1)

    if name in names:
        await ctx.send("you have already signed up for this raid!")
        return

    raid_worksheet.insert_row([name, wow_class, role, str(datetime.now())])
    await ctx.send("you have been signed up")

bot.run(config["keys"]["DiscordSecret"])
