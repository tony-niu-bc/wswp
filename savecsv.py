#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

class SaveCSV:

    def __init__(self, filename):
        self.writer = csv.writer(open('%s.csv' % filename, 'wb'))

    def __call__(self, row):
        self.writer.writerow(row)