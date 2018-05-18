"""service file"""
import os

import praw

try:
    from jbp_bot import JbpBot
except ModuleNotFoundError:
    from .jbp_bot import JbpBot

def main() -> None:
    """main service function"""

    reddit: praw.Reddit = praw.Reddit(
        client_id=os.environ["jbp_bot_client_id"],
        client_secret=os.environ["jbp_bot_client_secret"],
        refresh_token=os.environ["jbp_bot_refresh_token"],
        user_agent="linux:jbp_bot:v1.0 (by /r/Neoliberal)"
    )

    bot: JbpBot = JbpBot(
        reddit,
        os.environ["jbp_bot_subreddit"]
    )

    while True:
        bot.listen()

    return

if __name__ == "__main__":
    main()
