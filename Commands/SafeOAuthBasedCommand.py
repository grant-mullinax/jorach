from discord.ext import commands
from gspread.exceptions import APIError

from DataProviders.GoogleCredentialProvider import get_google_credentials


class SafeOAuthBasedCommand(commands.Cog):
    """
    `SafeOAuthBasedCommand` is an Cog-inheriting class that allows Google OAuth-based commands to automatically refresh
    their access tokens.

    To conform to this pseudo-interface, you must do the following:
    - Have a class inherit from `SafeOAuthBasedCommand`
    - Create a bot command that calls `execute(self, ctx, params)`
    - Add a function definition for `__run_command(self, ctx, params)`.

    Example:
    ```
    class ExampleCommand(SafeOAuthBasedCommand):
        @bot.command(name="do" description="example"
        async def do_it(self, ctx, param1, param2):
            await self.execute(ctx, [param1, param2])

        async def run_command(self, ctx, params):
            await do_something_stupid()
    ```

    To run your command with automatic oAuth token refresh, simply run `instance.execute(params)`
    """

    async def execute(self, ctx, params, retry=True):
        """
        Executes the command specific in `__run_command`. If the command fails due to an oAuth token exception
        and `retry` is `True`, then a new token is fetched and `__run_command` is ran again.

        Calls `__run_command(ctx, params)` with the same parameters as this was called with.

        :param ctx: The invocation context. Assumed to be a valid Discord bot context.
        :param params: The parameters of the OAuthBasedCommand.
        :param retry: A boolean specifying whether or not to retry the command
        """

        try:
            await self.run_command(ctx, params)
        except APIError as exception:
            if retry:
                get_google_credentials().login()

                # Failed; refetch credentials and retry this function again.
                # Set this call to not retry, as we don't want to infinitely loop.
                await self.execute(ctx, params, retry=False)
            else:
                print("Error in class named [%s]. Either unable to refresh token or another exception occurred.")
                await ctx.send(
                    "Sorry, I reached an error! Please verify your parameters were correct, and try again.\n"
                    + "If this problem persists, please contact my developer."
                )
                raise exception
        return

    async def run_command(self, ctx, params):
        """

        :param ctx:
        :param params: An Array of the parameters that were specified. Nullable.
        :return:
        """
        raise Exception("Body for run_command should be implemented in child class.")
