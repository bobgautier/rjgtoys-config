
import argparse
import os

from rjgtoys.config import Config, getConfig

class MyConfig(Config):

    a: str
    b: str
    c: str

cfg = getConfig(MyConfig)

def main():

    p = argparse.ArgumentParser() #'example1')

    cfg.add_arguments(p, default='ex4.yaml', adjacent_to=__file__)
    p.parse_args()

    print(f"Configured a={cfg.a} b={cfg.b} c={cfg.c}")

if __name__ == "__main__":
    main()
