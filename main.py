import discord
import secret
from discord.ext import commands
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("Jorach-5b2d048d0abd.json", scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key("1xOtoOyKbesB-EOqKLvfv6cB_oj30pr_LYlFZ_BkuqwU")
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
        print(discord_ids.index(author_hash))
        identity_worksheet.delete_row(discord_ids.index(author_hash) + 1)  # sheets is indexed starting at 1

    identity_worksheet.append_row([hash(ctx.author), author_hash, name, wow_class, role])
    await ctx.send("your identity has been saved")


@bot.command()
async def register(ctx, raid_name: str):
    discord_ids = identity_worksheet.col_values(1)
    author_hash = str(hash(ctx.author))

    if author_hash not in discord_ids:
        await ctx.send("your identity has not been saved! please use the !identity command")
        return

    worksheets = spreadsheet.worksheets()
    raid_names = map(lambda ws: ws.title, worksheets)
    if raid_name not in raid_names:
        await ctx.send("that is not a valid raid! valid raids are: " + str(raid_names))
        return

    raid_worksheet = spreadsheet.worksheet(raid_name)

    values = identity_worksheet.row_values(discord_ids.index(author_hash) + 1)
    raid_worksheet.insert_row([values[2], values[3], values[4], str(datetime.now())])  # name, class, and role
    await ctx.send("you have been signed up")

bot.run(secret.discord_token)
