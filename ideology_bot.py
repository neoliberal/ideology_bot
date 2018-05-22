"""main class"""
import logging
import signal
import random
import pickle
from typing import Deque, List, Dict, Any

import praw
from slack_python_logging import slack_logger

from ideology import Ideology


class IdeologyBot(object):
    """Replies to users with a ideological response"""
    __slots__ = ["reddit", "logger", "ideologies"]

    def __init__(self, reddit: praw.Reddit) -> None:
        """initialize"""

        def register_signals() -> None:
            """registers signals"""
            signal.signal(signal.SIGTERM, self.exit)

        self.logger: logging.Logger = slack_logger.initialize("ideology_bot")
        self.logger.debug("Initializing")
        self.reddit: praw.Reddit = reddit
        self.ideologies: Dict[str, Ideology] = self._read_ideologies()
        register_signals()
        self.logger.info("Successfully initialized")

    def _read_ideologies(self) -> Dict[str, Ideology]:
        """reads ideologies from the /data folder"""
        from pathlib import Path
        import json

        self.logger.debug("Attempting to read all ideology files")
        ideologies: Dict[str, Ideology] = {}
        for file in Path('data').glob('*.json'):
            with file.open('r') as ideology:
                parsed: Dict[str, Dict[str, Any]] = json.loads(ideology.read())
                trigger, data = list(parsed.items())[0]
                ideologies[trigger] = Ideology(*data.values())
        return ideologies

    def exit(self, signum: int, frame) -> None:
        """defines exit function"""
        import os
        _ = frame
        self.logger.info("Exited gracefully with signal %s", signum)
        os._exit(os.EX_OK)
        return

    def listen(self) -> None:
        """lists to subreddit's comments for JBP requests"""
        import prawcore
        from time import sleep
        try:
            for mention in praw.models.util.stream_generator(
                    self.reddit.inbox.unread):
                self.handle_mention(mention)
        except prawcore.exceptions.ServerError:
            self.logger.error("Server error: Sleeping for 1 minute.")
            sleep(60)
        except prawcore.exceptions.ResponseException:
            self.logger.error("Response error: Sleeping for 1 minute.")
            sleep(60)
        except prawcore.exceptions.RequestException:
            self.logger.error("Request error: Sleeping for 1 minute.")
            sleep(60)

    def handle_mention(self, mention: praw.models.Comment) -> None:
        """handles parsing and reply"""
        self.logger.debug("Found potential mention")
        split: List[str] = mention.body.lower().split()
        for trigger, ideology in self.ideologies.items():
            if trigger in split:
                self.logger.debug("ideology request found in %s", str(mention))
                try:
                    mention.reply(ideology.generate())
                    return
                except:
                    self.logger.error("Reply failed to comment: %s",
                                      str(mention))
