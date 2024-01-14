import logging
from ..settings import fitbit_constants as cte
from datetime import datetime


class AppLogger(object):
    """
    Configure the logging module of python.
    AppLogger is to be call, which set the python's module.
    Then, just import the logging module in your modules
    """

    def __init__(self):
        """
        Configure the logging module of python.
        """
        super().__init__()

        # configure the logger
        self._config_logger()
        logging.info("The logger has been configured")

    @staticmethod
    def _config_logger():
        log_name = '../../logs/{:%Y-%m-%d}.txt'.format(datetime.now())
        logging.basicConfig(filename=log_name,
                            format='%(asctime)s %(message)s',
                            datefmt=cte.ISO_COMPLETE,
                            level=logging.DEBUG)

# ==================================================================70
# leave a blank line below
