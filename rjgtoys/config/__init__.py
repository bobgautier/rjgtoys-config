"""

Config mechanism exports

"""

from rjgtoys.config._config import Config
from rjgtoys.config._proxy import ConfigProxy
from rjgtoys.config._manager import ConfigManager

#
# Create a name for ConfigProxy that's reminiscent of
# logging.getLogger
#

getConfig = ConfigProxy
