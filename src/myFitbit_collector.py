"""
Created on Oct 28, 2017

@author: fairvel
"""
import credentials

from coreFunctions.data_collector import DataCollector


fitbit_collector = DataCollector(credentials.client_id, credentials.client_secret)
fitbit_collector.get_credentials()
fitbit_collector.collect_data_from_fitbit()
