#!/usr/bin/env python

import sys
import os
import re
from subprocess import check_output
from datetime import datetime
from datetime import timedelta
import time
import calendar
import json

def unixtime_to_string(unixtime, offset_minute=0):
  dt = datetime.utcfromtimestamp(unixtime) + timedelta(0, offset_minute * 60)
  offset_sign = '+'
  if offset_minute < 0:
    offset_sign = '-'
    offset_minute = abs(offset_minute)
  offset_hour = offset_minute / 60
  offset_minute = offset_minute % 60
  return '{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}{}{:02d}:{:02d}'.format(
    dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
    offset_sign, offset_hour, offset_minute)

def unixtime_from_string(string):
  regex = re.compile(r'(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)(\+|-)(\d+):(\d+)')
  m = regex.match(string)
  if not m:
    raise Exception('invalid format')
  year = int(m.group(1))
  month = int(m.group(2))
  day = int(m.group(3))
  hour = int(m.group(4))
  minute = int(m.group(5))
  second = int(m.group(6))
  offset = (int(m.group(8)) * 60 + int(m.group(9))) * 60
  if m.group(7) == '-':
    offset *= -1
  dt = datetime(year, month, day, hour, minute, second) - timedelta(0, offset)
  return calendar.timegm(dt.utctimetuple())

def get_timezone_offset():
  return - time.timezone / 60

class App:
  __repo_dir = None

  def filename_filter_func(self, filename):
    if filename.startswith('.'):
      return False
    return True

  def filter_filenames(self, filenames):
    return filter(lambda x: self.filename_filter_func(x), filenames)

  def main(self, args):
    if len(args) < 2:
      raise Exception('command not specified')

    command = args[1]
    method_name = 'main_' + command
    method = getattr(self, method_name, None)
    if not method:
      raise Exception('command {} does not exists'.format(command))
    method(args[2:])

  def main_store(self, args):
    for dirpath, dirnames, filenames in os.walk('.'):
      dirnames[:] = self.filter_filenames(dirnames)
      filenames = sorted(self.filter_filenames(filenames))
      json_data = []
      for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        mtime = os.path.getmtime(filepath)
        mtime_str = unixtime_to_string(mtime, get_timezone_offset())
        json_data.append({
          'name': filename,
          'mtime': mtime_str})
      json_str = json.dumps(json_data, indent=2)
      json_path = os.path.join(dirpath, '.mtime_sync.json')
      with open(json_path, 'w') as f:
        f.write(json_str)

  def main_load(self, args):
    for dirpath, dirnames, filenames in os.walk('.'):
      dirnames[:] = self.filter_filenames(dirnames)

      json_path = os.path.join(dirpath, '.mtime_sync.json')
      if not os.path.isfile(json_path):
        continue

      json_str = ''
      with open(json_path, 'r') as f:
        json_str = f.read()
      json_data = json.loads(json_str)
      for json_record in json_data:
        filename = json_record['name']
        filepath = os.path.join(dirpath, filename)
        if os.path.exists(filepath):
          mtime_str = json_record['mtime']
          mtime = unixtime_from_string(mtime_str)
          atime = time.time()
          os.utime(filepath, (atime, mtime))

app = App()
app.main(sys.argv)