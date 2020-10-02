
import argparse

from rjgtoys.config import getConfig, Config

class MyConfig(Config):

    x: int = 1


cfg = getConfig(MyConfig)

def main():

    p = argparse.ArgumentParser('example')

    cfg.add_arguments(p, default='example3.yaml')

    args = p.parse_args()
    print(f"Args: {args}")


    print(f"Config: {cfg.x}")

main()

