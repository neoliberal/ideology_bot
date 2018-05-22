"""service file"""
import os

import praw

try:
    from ideology_bot import IdeologyBot
except ModuleNotFoundError:
    from .ideology_bot import IdeologyBot


def main() -> None:
    """main service function"""

    reddit: praw.Reddit = praw.Reddit(
        client_id=os.environ["ideology_bot_client_id"],
        client_secret=os.environ["ideology_bot_client_secret"],
        refresh_token=os.environ["ideology_bot_refresh_token"],
        user_agent="linux:jbp_bot:v1.0 (by /r/Neoliberal)")

    bot: IdeologyBot = IdeologyBot(
        reddit
    )

    while True:
        bot.listen()

    return

if __name__ == "__main__":
    main()
