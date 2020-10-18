# jorach

## config.ini:
Create a config.ini file in the root directory. This file is used to pass the tokens to the necessary services.

Format:
```
[default]
SpreadsheetId = <YourSpreadsheetIdHere>

[keys]
DiscordSecret = <YourDiscordBotSecretHere>
GoogleCredentialsFile = <PathToGoogleCredentialsFileHere (e.g.: account.json)>
```

To test, you will have to supply your own discord secret, spreadsheet id, and google credentials.
- Get a google credentials file from https://gspread.readthedocs.io/en/latest/oauth2.html
    - IMPORTANT: Add the account you create here to your spreadsheet's "edit access" list!
    - Example email: sheets@jorach-256403.iam.gserviceaccount.com
        - In the spreadsheet, click "Share", enter the email generated, and give it edit access
- Get Discord bot secret key from https://discord.com/developers/applications/
- The spreadsheet ID can be the ID of any spreadsheet; Jorach will handle the formatting.
    - [How to retrieve a spreadsheet ID](https://stackoverflow.com/questions/36061433/how-to-do-i-locate-a-google-spreadsheet-id)