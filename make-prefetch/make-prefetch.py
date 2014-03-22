#!/usr/bin/env python

from argparse import ArgumentParser
import hashlib
import os
import sys

usage = """make-prefetch.py [options] <file>

Create a prefetch statement for IBM Endpoint Manager ActionScript

Options:
  -a, --algorithm ALGORITHM    Hash algorithm to use (all, sha1, sha256)
                               default: all
  -o, --output OUTPUT          Output format (prefetch, davis, value)
                               default: prefetch
  -h, --help                   Print this help message and exit

Examples:
  Create a 9.1 style pretch statement

    make-prefetch.py hello.txt

  Create a 9.0 style prefetch statement

    make-prefetch.py --algorithm sha1 hello.txt

  Create a 7.2 style prefetch statement

    make-prefetch.py --algorithm sha1 --output davis hello.txt
"""

def hash_file(args):
  f = open(args.file, 'rb')

  sha1 = hashlib.sha1()
  sha256 = hashlib.sha256()

  while True:
    chunk = f.read(4096)
    if not chunk:
      break
    sha1.update(chunk)
    sha256.update(chunk)

  f.close()
  return {
    'name': os.path.basename(args.file),
    'url': 'http://REPLACEME',
    'size': os.path.getsize(args.file),
    'sha1': sha1.hexdigest(),
    'sha256': sha256.hexdigest()
  }

def prefetch_output(algorithm):
  if args.algorithm == 'sha256':
    return "prefetch {name} size:{size} {url} sha256:{sha256}"
  if args.algorithm == 'sha1':
    return "prefetch {name} sha1:{sha1} size:{size} {url}"
  return "prefetch {name} sha1:{sha1} size:{size} {url} sha256:{sha256}"

def davis_output(algorithm):
  if algorithm != 'all' and algorithm != 'sha1':
    print("Algorithm {0} is not supported in davis downloads".format(algorithm))
    sys.exit(2)
  return ("begin prefetch block\n"
          "add prefetch item name={name} sha1={sha1} size={size} url={url}\n"
          "collect prefetch items\n"
          "end prefetch block")

def value_output(algorithm):
  if algorithm == 'sha1':
    return "{sha1}"
  if algorithm == 'sha256':
    return "{sha256}"
  print("You must specify a hash algorithm to use")
  sys.exit(2)

parser = ArgumentParser(add_help=False, usage=usage)

parser.add_argument('file')

parser.add_argument(
  '-a',
  '--algorithm',
  choices=['all', 'sha1', 'sha256'],
  default='all')

parser.add_argument(
  '-o',
  '--output',
  choices=['value', 'davis', 'prefetch'],
  default='prefetch')

if '-h' in sys.argv or '--help' in sys.argv:
  print(usage)
  sys.exit()

args = parser.parse_args()

file = hash_file(args)

if args.output == 'value':
  output = value_output(args.algorithm)
elif args.output == 'davis':
  output = davis_output(args.algorithm)
else:
  output = prefetch_output(args.algorithm)

print(output.format(name=file['name'],
                    size=file['size'],
                    url=file['url'],
                    sha1=file['sha1'],
                    sha256=file['sha256']))