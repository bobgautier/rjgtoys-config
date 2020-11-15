
import argparse
import os

from rjgtoys.config import getConfig, Config

class MyConfig(Config):

    x: int = 1


cfg = getConfig(MyConfig)

def main():

    p = argparse.ArgumentParser('example')

    cfg.add_arguments(p, default=os.path.join(os.path.dirname(__file__), 'ex3.yaml'))

    args = p.parse_args()
    print(f"Args: {args}")


    print(f"Config: {cfg.x}")

main()

