"""
examples/translate.py: translate words using a dictionary
"""

import argparse
import os
from typing import Dict

from rjgtoys.config import Config, getConfig

class TranslateConfig(Config):

    words: Dict[str, str]

#cfg = getConfig(TranslateConfig)

cfg = TranslateConfig.value()

def main(argv=None):

    p = argparse.ArgumentParser()

    cfg.add_arguments(p, default='translate.yaml', adjacent_to=__file__)
    args, tail = p.parse_known_args(argv)

    for word in tail:
        result = cfg.words.get(word, "I don't know that word")
        print(f"{word}: {result}")


if __name__ == "__main__":
    main()
