
import argparse
import os

from rjgtoys.config import Config, getConfig

class MyConfig(Config):

    name: str = "Noname"

    param: int

cfg = getConfig(MyConfig)

def main():

    p = argparse.ArgumentParser() #'example1')

    cfg.add_arguments(p, default=os.path.join(os.path.dirname(__file__), 'ex1a.yaml'))
    p.parse_args()

    print("Configured name: %s" % (cfg.name))
    print("Configured param: %s" % (cfg.param))

if __name__ == "__main__":
    main()
