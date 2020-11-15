
import argparse
from typing import Dict, List
from rjgtoys.config import Config, getConfig

# Step One: declare configuration parameters

class MailerConfig(Config):

    target_lists: Dict[str, List[str]]

# Step Two: connect to the configuration system

cfg = getConfig(MailerConfig)

# Step Three: use the data

def get_recipients(list_name):
    """Returns the list of members of a mailing list."""

    return cfg.target_lists[list_name]


def main(argv=None):
    parser = argparse.ArgumentParser('Send a message to a mailing list')

    parser.add_argument('--list', type=str, help="Name of the list")

    cfg.add_arguments(parser, default='mailer.conf', adjacent_to=__file__)

    args = parser.parse_args(argv)

    # Hack: force loading

    cfg.value

    print(f"Mail will be sent to mailing list {args.list}:")

    for member in get_recipients(args.list):
        print(f"   {member}")

if __name__ == "__main__":
    main()
