import configparser
import os
import sys
import datetime

from fitbitDataloader.coreFunctions.gather_keys_oauth2 import OAuth2Server
from fitbitDataloader.settings import fitbit_constants as cte
import fitbit


class SettingsManager(object):
    """Everything about the settings of the application"""

    def __init__(self):
        super().__init__()
        """Prepare the properties"""
        self.config = configparser.ConfigParser()
        self.here = os.path.dirname(os.path.realpath(__file__))
        self.config_filename = cte.FILE_SETTINGS

        # Authorisation and access
        self.client_id = None
        self.client_secret = None
        self.server = None
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.auth2_client = None
        self.got_credentials = False

        self.request_counter_limit = None
        self.databases_location = None
        self.initial_date = None
        self.date_format_for_request = cte.ISO_FORMAT
        self.date_format_for_file = cte.ISO_COMPACT

        self.todayDate = datetime.datetime.today()
        self.yesterday = self.todayDate - datetime.timedelta(days=1)

    def read_settings(self) -> bool:
        if not self.config.read(os.path.join(self.here, self.config_filename)):
            return False

        self.client_id = self.config['fitbit_auth']['client_id']
        self.client_secret = self.config['fitbit_auth']['client_secret']
        self.request_counter_limit = int(self.config['fitbit_settings']['number_of_request_per_hour'])
        self.pause_delay = int(self.config['fitbit_settings']['pause_period_second'])

        self.databases_location = self.config['folders']['data_location_windows']
        if sys.platform == "linux":
            self.databases_location = self.config['folders']['data_location_linux']

        self.initial_date = datetime.datetime.strptime(self.config['date_time']['initial_date'],
                                                       self.date_format_for_request)
        return True

    def get_credentials(self) -> bool:
        """
        A couple of tokens are to be collected before getting access
        For obtaining Access-token and Refresh-token
        """
        self.server = OAuth2Server(self.client_id, self.client_secret)
        self.server.browser_authorize()

        self.access_token = str(self.server.fitbit.client.session.token['access_token'])
        self.refresh_token = str(self.server.fitbit.client.session.token['refresh_token'])
        self.expires_at = str(self.server.fitbit.client.session.token['expires_at'])
        self.auth2_client = fitbit.Fitbit(self.client_id, self.client_secret, oauth2=True,
                                          access_token=self.access_token, refresh_token=self.refresh_token)

        self.got_credentials = bool(self.auth2_client)
        return self.got_credentials

# ==================================================================70
# leave a blank line below
