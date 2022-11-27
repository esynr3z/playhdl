from . import utils

import rich.traceback

rich.traceback.install(show_locals=False)


__version__ = utils.get_pkg_version()
