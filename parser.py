#!/usr/bin/env python2.7

from __future__ import unicode_literals
import sys
import csv
import re
import pytz
import datetime

# Set default encoding as utf-8
reload(sys)
sys.setdefaultencoding('utf-8')

# Error handling
class Errors(Exception):
    def __init__(self, field, value, message):
        super(Errors, self).__init__(
            "Error normalizing {}={!r}: {!r}".format(field, value, message)
        )

# Timestamp normalization function
#
# The Timestamp column should be formatted in ISO-8601 format.
# The Timestamp column should be assumed to be in US/Pacific time; please convert it to US/Eastern.
#
def norm_timestamp(timestamp):
    try:
        USPacific = pytz.timezone('US/Pacific')
        USEastern = pytz.timezone('US/Eastern')
        ts = datetime.datetime.strptime(timestamp, "%m/%d/%y %H:%M:%S %p")
        ts_iso = USPacific.localize(ts).astimezone(USEastern).isoformat()
        return ts_iso
    except Exception as e:
        raise Errors('Timestamp', timestamp, e)

# Address normalization function
#
# The Address column should be passed through as is, except for Unicode validation. Please note there are commas in the Address field; your CSV parsing will need to take that into account. Commas will only be present inside a quoted string.
#
def norm_addr(addr):
    try:
        return addr
    except Exception as e:
        raise Errors('Address', addr, e)

# Zip normalization function
#
# All ZIP codes should be formatted as 5 digits.
# If there are less than 5 digits, assume 0 as the prefix.
#
def norm_zip(zip):
    try:
        return '{0:0>5}'.format(zip)
    except Exception as e:
        raise Errors('ZIP', zip, e)

# Name normalization function
#
# All name columns should be converted to uppercase.
# There will be non-English names.
#
def norm_name(name):
    try:
        return name.upper()
    except Exception as e:
        raise Errors('FullName', name, e)

# Duration normalization function
#
# The columns `FooDuration` and `BarDuration` are in HH:MM:SS.MS format (where MS is milliseconds); please convert them to a floating point seconds format.
#
def norm_duration(field_name, duration):
    try:
        h, m, s, ms = map(int, re.split(r'[:\.]', duration))
        td = datetime.timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)
        secs = td.total_seconds()
        return float(secs)
    except Exception as e:
        raise Errors(field_name, duration, e)

# Notes normalization function
#
# The column "Notes" is free form text input by end-users; please do not perform any transformations on this column. If there are invalid UTF-8 characters, please replace them with the Unicode Replacement Character.
#
def norm_notes(notes):
    try:
        decoded_unicode = notes.decode('utf-8', 'replace')
        return decoded_unicode
    except Exception as e:
        raise Errors('Notes', notes, e)

# Run each function per cell
def norm_row(row):
    row[0] = norm_timestamp(row[0])
    row[1] = norm_addr(row[1])
    row[2] = norm_zip(row[2])
    row[3] = norm_name(row[3])
    foo_duration = norm_duration('FooDuration', row[4])
    bar_duration = norm_duration('BarDuration', row[5])
    row[4] = foo_duration
    row[5] = bar_duration
    row[6] = foo_duration + bar_duration
    row[7] = norm_notes(row[7])
    return row

# Read input file, normalize per row, output to file
if __name__ == '__main__':
    input = open(sys.argv[1], 'rb')
    reader = csv.reader(input)
    next(reader) # Skip header row. Move to first row
    output = open(sys.argv[2], 'w')
    writer = csv.writer(output)
    for row in reader:
        try:
            writer.writerow(norm_row(row))
        except Errors as e:
            sys.stderr.write('Warning: {}\n'.format(e))
