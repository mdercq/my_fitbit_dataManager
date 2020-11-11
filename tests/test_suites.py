#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Describe here module purpose.

Author = "mdercq"
Organization = "Schlumberger - Geoservices - Interpretation Department"
Contact = "mdercq@slb.com"
Creation date = "2018-11-19"
Version = '0.1'

History
2018-11-19: initial creation
"""
from os import path
import inspect
from unittest import TestCase
from coreFunctions.data_collector import DataCollector


# write your code below
class TestSuite(TestCase):
    def setUp(self):
        """Prepare the necessary tools for the test suite"""
        self.collector = DataCollector()

    def test_01_instance(self):
        print(inspect.stack()[0][3])
        self.assertTrue(isinstance(self.collector, DataCollector))

    def test_02_get_files_in_container(self):
        print(inspect.stack()[0][3])
        self.collector.databases_location = r'/media/mdercq/sedentaire/Nomade/15_datasets/fitbit_data'
        self.collector._get_files_in_container('intraday_heart')

    def test_03_get_last_collected_date(self):
        print(inspect.stack()[0][3])
        self.collector.databases_location = r'/media/mdercq/sedentaire/Nomade/15_datasets/fitbit_data'
        list_of_files = self.collector._get_files_in_container('intraday_heart')
        last_collected_date = self.collector._get_last_collected_date(list_of_files)
        print(last_collected_date)

    def test_04_get_last_collected_date(self):
        print(inspect.stack()[0][3])
        self.collector.databases_location = r'/media/mdercq/sedentaire/Nomade/15_datasets/fitbit_data'
        list_of_files = self.collector._get_files_in_container('intraday_heart')
        last_collected_date = self.collector._get_last_collected_date(list_of_files)
        first_date_to_collect = self.collector._first_date_to_collect(last_collected_date)
        list_of_dates = self.collector._date_range(first_date_to_collect, self.collector.yesterday())
        print(list_of_dates)


# keep 1 blank line
