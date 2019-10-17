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

bot = commands.Bot(command_prefix="!", description=
"""My name is Jorach Ravenholdt and I'm here to help YOU raid.
Get started by using the !identity command.
!identity <name> <wow_class> <role>

look at my insides at
https://github.com/grant-mullinax/jorach
""")

wow_classes = ["druid", "hunter", "mage", "paladin", "priest", "rogue", "warlock", "warrior"]
available_roles = ["dps", "tank", "healer"]


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.command()
async def roles(ctx):
    await ctx.send("Valid roles are: " + str(available_roles))
    return


@bot.command()
async def sheet(ctx):
    await ctx.send(
        "See the spreadsheet at:\n https://docs.google.com/spreadsheets/d/" + config["default"]["SpreadsheetId"])
    return


@bot.command()
async def identity(ctx, name: str, wow_class: str, role: str):
    if wow_class.lower() not in wow_classes:
        await ctx.send("Invalid class name.")
        return

    if role.lower() not in available_roles:
        await ctx.send("Invalid role, valid roles are " + str(roles))
        return

    discord_ids = identity_worksheet.col_values(1)
    author_hash = str(hash(ctx.author))

    if author_hash in discord_ids:
        identity_worksheet.delete_row(discord_ids.index(author_hash) + 1)  # sheets is indexed starting at 1

    identity_worksheet.append_row([author_hash, str(ctx.author), name.lower(), wow_class.lower(), role.lower()])
    await ctx.send("Your identity has been recorded.")


@bot.command()
async def onyattunement(ctx, attuned: bool):
    discord_ids = identity_worksheet.col_values(1)
    author_hash = str(hash(ctx.author))

    if author_hash not in discord_ids:
        await ctx.send("Your identity has not been recorded! Please use the !identity command")
        return

    identity_worksheet.update_cell(discord_ids.index(author_hash) + 1, 6, str(attuned))
    await ctx.send("Your attunement has been recorded.")


@bot.command()
async def register(ctx, raid_name: str):
    raid_name_lower = raid_name.lower()

    if raid_name_lower == "identity":
        await ctx.send("nice try")
        return

    discord_ids = identity_worksheet.col_values(1)
    author_hash = str(hash(ctx.author))

    if author_hash not in discord_ids:
        await ctx.send("Your identity has not been recorded! Please use the !identity command")
        return

    worksheets = spreadsheet.worksheets()
    raid_names = map(lambda ws: ws.title, worksheets)
    if raid_name_lower not in raid_names:
        await ctx.send("That is not a valid raid! valid raids are: " + str(raid_names))
        return

    raid_worksheet = spreadsheet.worksheet(raid_name_lower)
    identity_values = identity_worksheet.row_values(discord_ids.index(author_hash) + 1)

    name, wow_class, role = (identity_values[2], identity_values[3], identity_values[4])
    names = raid_worksheet.col_values(1)

    if name in names:
        await ctx.send("You have already signed up for this raid!")
        return

    # hacky workaround for append row not working here
    raid_worksheet.insert_row([name, wow_class, role, str(datetime.now())], len(names) + 1)
    await ctx.send("Your availability has been noted for the upcoming raid.")


bot.run(config["keys"]["DiscordSecret"])
