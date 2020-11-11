"""
Created on Oct 28, 2017
@author: fairvel
"""
from src.coreFunctions.data_collector import DataCollector

fitbit_collector = DataCollector()
fitbit_collector.read_settings()
fitbit_collector.get_credentials()
fitbit_collector.collect_data()

