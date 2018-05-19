"""main class"""
import logging
import signal
import random
import pickle
from typing import Deque, List, Optional, Callable, Dict, Tuple

import praw
from slack_python_logging import slack_logger

class Ideology(object):
    __slots__ = ["trigger", "villians", "verbs", "favorites", "weapons",
                 "conclusions", "random", "name"]
    def __init__(self, trigger: str = "", name: str = "", villians: List[str] = [],
                 verbs: List[str] = [], favorites: List[str] = [],
                 weapons: List[str] = [], conclusions: List[str] = [],
                 random: List[str] = []):
        self.trigger = trigger
        self.name = name
        self.villians = villians
        self.verbs = verbs
        self.favorites = favorites
        self.weapons = weapons
        self.conclusions = conclusions
        self.random = random

    def generate(self) -> str:
        r: int = random.randint(0,100)
        for index in range(0, len(self.random)):
            if r < (index + 1) * 3:
                return f"{self.name}: \"{self.random[index]}\""
        villian:    str = random.choice(self.villians)
        verb:       str = random.choice(self.verbs)
        favorite:   str = random.choice(self.favorites)
        weapon:     str = random.choice(self.weapons)
        conclusion: str = random.choice(self.conclusions)
        response:   str = f"The wise {self.name} bowed his head solemnly and spoke: \"{villian} {verb} {favorite} {weapon}{conclusion}\""
        return response

class JbpBot(object):
    """Replies to users with a Petersonian response"""
    __slots__ = ["reddit", "subreddit", "config", "logger", "parsed", "ideologies"]

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
        self.parsed: Deque[str] = self.load()
        register_signals()
        self.ideologies: List[ideology] = self._create_lists()
        random.seed()
        self.logger.info("Successfully initialized")

    def exit(self, signum: int, frame) -> None:
        """defines exit function"""
        import os
        _ = frame
        self.save()
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
                if str(comment) in self.parsed:
                    continue
                else:
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

        for ideology in self.ideologies:
            if ideology.trigger in split:
                self.logger.debug("ideology request found in %s", str(comment))
                reply: str = ideology.generate()
                self.logger.debug(reply)
                try:
                    comment.reply(reply)
                    return
                except:
                    self.logger.error("Reply failed to comment: %s", str(comment))

    def save(self) -> None:
        """pickles tracked comments after shutdown"""
        self.logger.debug("Saving file")
        with open("jbp_parsed.pkl", 'wb') as parsed_file:
            parsed_file.write(pickle.dumps(self.parsed))
            self.logger.debug("Saved file")
            return
        return

    def load(self) -> Deque[str]:
        """loads pickle if it exists"""
        self.logger.debug("Loading pickle file")
        try:
            with open("jbp_parsed.pkl", 'rb') as parsed_file:
                try:
                    parsed: Deque[str] = pickle.loads(parsed_file.read())
                    self.logger.debug("Loaded pickle file")
                    self.logger.debug("Current Size: %s", len(parsed))
                    if parsed.maxlen != 10000:
                        self.logger.warning(
                            "Deque length is not 10000, returning new one")
                        return Deque(parsed, maxlen=10000)
                    self.logger.debug("Maximum Size: %s", parsed.maxlen)
                    return parsed
                except EOFError:
                    self.logger.debug("Empty file, returning empty deque")
                    return Deque(maxlen=10000)
        except FileNotFoundError:
            self.logger.debug("No file found, returning empty deque")
            return Deque(maxlen=10000)

    def _create_lists(self) -> List[Ideology]:
        ids: List[Ideology] = []
        ids.append(Ideology(
            trigger = "!JBP",
            name = "professor",
            villians = [
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
                "Millenials with a victimhood mentality"],
            verbs = [
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
                "feminize and weaken"],
            favorites = [
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
                "the humble lobster's quest"],
            weapons = [
                "because of their murderous equity doctrine",
                "because of their dangerous dreams of egalitarian utopia",
                "because of their hatred of Objective truth",
                "because of compelled speech",
                "because of their group identity",
                "because of their Maoist pronouns",
                "because of their propaganda from *Frozen*",
                "because of their radical collectivism",
                "because of their lens of power for everything",
                "because of their disdain for Being",
                "because of the ideological bill C-16",
                "because of their low serotonin levels and poor posture",
                "because of their totalitarian ideology which I've been studying for decades"],
            conclusions = [
                ", and we can't even have a conversation about it!",
                ", so just ask the Kulaks how that worked out.",
                ", and no one is talking about it!",
                ", as you can bloody well imagine!",
                ", just like Nietzche prophesized.",
                ", so you should sign up for the Self Authoring Suite.",
                ". [ignoring the original question] So let me ask you this...",
                ", and you can be damn sure about that!",
                ", which is why we need forced monogamy.",
                ", and it's a form of leftist tyrany."],
            random = [
                "[BEWARE THE CHAOS DRAGON!](https://i.imgur.com/yUrGKPX.png)",
                "Please donate to my Patreon, 80K/month isn't enough to defeat the leftists"]))
        ids.append(Ideology(
            trigger = "!ANCAP",
            name = "ancap",
            villians = [
                "Idiot statists",
                "Liberals (aka socialists)",
                "Big Government and its cronies",
                "Politically correct liberal cucks",
                "Commie scum",
                "'Mainstream' economists",
                "Welfare queens"],
            verbs = [
                "continually stomp on",
                "have zero respect for",
                "refuse to acknowledge the primacy of",
                "use state education (propaganda) to bash",
                "keep on attacking",
                "violate",
                "enslave society by villianizing"],
            favorites = [
                "personal freedom",
                "the NAP",
                "the FACT that humans act purposefully",
                "basic human liberties",
                "Rothbard and Mises's genius",
                "the concept of private militaries",
                "Ayn Rand's literary genius",
                "my right to own McNukes",
                "Austrian Economics"],
            weapons = [
                "because of their addiction to the government teat",
                "with their \"government roads\"",
                "because of their refusal to accept mises.org as a source",
                "with their small, weak, socialist worldview",
                "because of their disrespect for property rights",
                "with their insistence on a functioning government(theft)",
                "because they desire to command and control others",
                "with 'anti pollution' regulation"],
            conclusions = [
                ", which makes them fascists.",
                ", which illustrates the need for private police.",
                ", and they need to be physically removed.",
                ".  It's just common sense.",
                ", and it's practically Stalinism.",
                ", which is another form of slavery.",
                ".  Typical leeches and parasites.",
                ".  Btw, it's called Ehpebophilia.",
                ", just another form of tyranny.",
                ".  Fucking statists."],
            random = [
                "THE RESPONSE TO 1984 IS 1776",
                "WE ARE THE THREE PERCENT"]))
        return ids

'''
        ids.append(Ideology(
            trigger = "",
            name = "",
            villians = [
                ],
            verbs = [
                ],
            favorites = [
                ],
            weapons = [
                ],
            conclusions = [
                ],
            random = [
                ]))
'''
