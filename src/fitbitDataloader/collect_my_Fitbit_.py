"""
Created on Oct 28, 2017
@author: fairvel
"""
from fitbitDataloader.coreFunctions.data_collector import DataCollector


def main():
    fitbit_collector = DataCollector()
    fitbit_collector.read_settings()
    fitbit_collector.get_credentials()
    fitbit_collector.collect_data()


if __name__ == '__main__':
    main()

# **********************************************************************70
# leave one line
