"""ideology class, holds attributes"""
import random
from typing import NamedTuple, List


class Ideology(NamedTuple):
    """Ideology class"""
    name: str
    pronoun: str
    villians: List[str]
    verbs: List[str]
    favorites: List[str]
    weapons: List[str]
    conclusions: List[str]
    random: List[str]

    def generate(self) -> str:
        """generates a response given attributes"""
        rand: int = random.randint(0, 100)
        for index in range(0, len(self.random)):
            if rand < (index + 1) * 3:
                return f"{self.name}: \"{self.random[index]}\""

        villian: str = random.choice(self.villians)
        verb: str = random.choice(self.verbs)
        favorite: str = random.choice(self.favorites)
        weapon: str = random.choice(self.weapons)
        conclusion: str = random.choice(self.conclusions)
        return f"The wise {self.name} bowed {self.pronoun} head solemnly and spoke: \"{villian} {verb} {favorite} {weapon}{conclusion}\""
