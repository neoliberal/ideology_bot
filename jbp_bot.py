"""main class"""
from configparser import ConfigParser, ParsingError, NoSectionError
import logging
import signal
import random
from typing import List, Optional, Callable, Dict, Tuple

import praw
from slack_python_logging import slack_logger


class JbpBot(object):
    """Replies to users with a Petersonian response"""
    __slots__ = ["reddit", "subreddit", "config", "logger"]

    def __init__(self, reddit: praw.Reddit, subreddit: str) -> None:
        """initialize"""

        def register_signals() -> None:
            """registers signals"""
            signal.signal(signal.SIGTERM, self.exit)

        self.logger: logging.Logger = slack_logger.initialize("jbp_bot")
        self.logger.debug("Initializing")
        self.reddit: praw.Reddit = reddit
        self.subreddit: praw.models.Subreddit = self.reddit.subreddit(
            subreddit)
        register_signals()
        self._create_lists()
        random.seed()
        self.logger.info("Successfully initialized")

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
            for comment in self.subreddit.stream.comments(pause_after=1):
                if comment is None:
                    break
                self.handle_comment(comment)
        except prawcore.exceptions.ServerError:
            self.logger.error("Server error: Sleeping for 1 minute.")
            sleep(60)
        except prawcore.exceptions.ResponseException:
            self.logger.error("Response error: Sleeping for 1 minute.")
            sleep(60)
        except prawcore.exceptions.RequestException:
            self.logger.error("Request error: Sleeping for 1 minute.")
            sleep(60)

    def handle_comment(self, comment: praw.models.Comment) -> None:
        """handles parsing and reply"""
        split: List[str] = comment.body.upper().split()
        self.parsed.append(str(comment))

        if "!JBP" in split:
            self.logger.debug("JBP request found in %s", str(comment))
            try:
                comment.reply(self._jbp_generate())
            except:
                self.logger.error("Reply failed to comment: %s", str(comment)))

    def _jbp_generate(self) -> str:
        villian:    str = villians[random.randrange(0, len(villians))]
        verb:       str = verbs[random.randrange(0, len(verbs))]
        favorite:   str = favorites[random.randrange(0, len(favorites))]
        weapon:     str = weapons[random.randrange(0, len(weapons))]
        conclusion: str = conclusions[random.randrange(0, len(conclusions))]
        response:   str = f"The wise man bowed his head solemnly and spoke: \"{villian} {verb} {favorite} because of their {weapon} {conclusion}\""
        return response


    def _create_lists(self):
        self.villians: List[str] = [
            "Postmodern Neomarxists",
            "Feminists (who secretly crave domination)",
            "Leftist academics",
            "Dangerous idologues",
            "Derrida and Foucault",
            "Indoctrinated students",
            "Social justice types",
            "Radical trans activists",
            "Politically correct HR departments",
            "*Actual* Communists",
            "The *Left*",
            "Millenials with a victimhood mentality"
        ]
        self.verbs: List[str] = [
            "are totally corrupting",
            "have zero respect for",
            "want to annihilate",
            "assault the archetype of",
            "don't bloody believe in",
            "will quickly infect",
            "unleash the Chaos Dragon of",
            "dismiss and transgress",
            "must be stopped from attacking",
            "will make Gulags out of",
            "feminize and weaken"
        ]
        self.favorites: List[str] = [
            "the dominance hierarchy",
            "the metaphorical substrate",
            "Western values",
            "the classical humanities",
            "the individual",
            "the Hero's Journey",
            "the fabric of Being",
            "Solzhenitsyn's genius",
            "Carl Jung's legacy",
            "IQ testing's ability to determine achievement",
            "the divine Logos",
            "the inescapable tragedy and suffering of life",
            "the humble lobster's quest"
        ]
        self.weapons: List[str] = [
            "murderous equity doctrine",
            "dangerous egalitarian utopia",
            "hatred of Objective truth",
            "compelled speech",
            "group identity",
            "Maoist pronouns",
            "propaganda from *Frozen*",
            "radical collectivism",
            "lens of power for everything",
            "disdain for Being",
            "ideological bill C-16",
            "low serotonin levels and poor posture",
            "totalitarian ideology which I've been studying for decades"
        ]
        self.conclusions: List[str] = [
            "and we can't even have a conversation about it!",
            "so just ask the Kulaks how that worked out.",
            "and no one is talking about it!",
            "as you can bloody well imagine!",
            "just like Nietzche prophesized.",
            "so you should sign up for the Self Authoring Suite.",
            ". [ignoring the original question] So let me ask you this...",
            "and you can be damn sure about that!"
        ]
