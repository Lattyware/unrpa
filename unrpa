#!/usr/bin/env python2

'''
  This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import optparse
import sys
import pickle

class UnRPA:

	verbose = None
	path = None
	mkdir = None
	version = None
	archive = None

	def __init__(self, filename, verbosity=1, path=None, mkdir=False, version=None):
		self.verbose = verbosity
		if path:
			self.path = os.path.abspath(path)
		else:
			self.path = os.getcwd()
		self.mkdir = mkdir
		self.version = version
		self.archive = filename

	def extract_files(self):
		if self.verbose > 0:
			print("unrpa: extracting files.")
		if self.mkdir:
			self.make_directory_structure(self.path)
		if not os.path.isdir(self.path):
			sys.exit("unrpa: error: path doesn't exist, if you want to create it, use -m.")
		index = self.get_index()
		for item, data in index.iteritems():
			self.make_directory_structure(os.path.join(self.path, os.path.split(item)[0]))
			raw_file = self.extract_file(item, data)
			with open(os.path.join(self.path, item.encode('UTF-8')), "wb") as f:
				f.write(raw_file)

	def list_files(self):
		if self.verbose > 1:
			print("unrpa: listing files:")
		index = self.get_index()
		paths = index.keys()
		paths.sort()
		for path in paths:
			print(path)

	def extract_file(self, name, data):
		if self.verbose > 1:
			print("unrpa: extracting file: " + name)
		if len(data[0]) == 2:
			offset, dlen = data[0]
			start = ''
		else:
			offset, dlen, start = data[0]
		with open(self.archive, "rb") as f:
			f.seek(offset)
			raw_file = start + f.read(dlen - len(start))
		return raw_file

	def make_directory_structure(self, name):
		if self.verbose > 2:
			print("unrpa: creating directory structure:" + name)

		if not os.path.exists(name) and not os.path.isdir(name):
			os.makedirs(name)

	def get_index(self):
		if not self.version:
			if os.path.splitext(self.archive)[1].lower() == ".rpa":
				with open(self.archive, "rb") as f:
					self.version = self.determine_version(f.readline())
			elif os.path.splitext(self.archive)[1].lower() == ".rpi":
				self.version = 1
		if self.version == 3:
			with open(self.archive, "rb") as f:
				l = f.readline()
				offset = int(l[8:24], 16)
				key = int(l[25:33], 16)
				f.seek(offset)
				index = pickle.loads(f.read().decode("zlib"))
				index = self.deobfuscate_index(index, key)
		elif self.version == 2:
			with open(self.archive, "rb") as f:
				offset = int(f.readline()[8:], 16)
				f.seek(offset)
				index = pickle.loads(f.read().decode("zlib"))
		elif self.version == 1:
			with open(self.archive, "rb") as f:
				index = pickle.loads(f.read().decode("zlib"))
		else:
			sys.exit("unrpa: error: file doesn't look like an archive, if you are sure it is, use -f.")
		if not "/" == os.sep:
			final = {}
			for item, data in index.iteritems():
				final[item.replace("/", os.sep)] = data
			return final
		else:
			return index

	def determine_version(self, line):
		if line.startswith("RPA-3.0 "):
			return 3
		if line.startswith("RPA-2.0 "):
			return 2
		else:
			return None

	def deobfuscate_index(self, index, key):
		for k in index.keys():
			if len(index[k][0]) == 2:
				index[k] = [ (offset ^ key, dlen ^ key) for offset, dlen in index[k] ]
			else:
				index[k] = [ (offset ^ key, dlen ^ key, start) for offset, dlen, start in index[k] ]
		return index

if __name__ == "__main__":
	parser = optparse.OptionParser(usage = "usage: %prog [options] pathname", version="%prog 1.1")

	parser.add_option("-v", "--verbose", action="count", dest="verbose", help="explain what is being done [default]")
	parser.add_option("-s", "--silent", action="store_const", const=0, dest="verbose", default=1, help="make no output")
	parser.add_option("-l", "--list", action="store_true", dest="list", default=False, help="only list contents, do not extract")
	parser.add_option("-p", "--path", action="store", type="string", dest="path", default=None, help="will extract to the given path")
	parser.add_option("-m", "--mkdir", action="store_true", dest="mkdir", default=False, help="will make any non-existant directories in extraction path")
	parser.add_option("-f", "--force", action="store", type="int", dest="version", default=None, help="forces an archive version. May result in failure.")

	(options, args) = parser.parse_args()

	if not len(args) == 1:
		if options.verbose:
			parser.print_help()
		parser.error("incorrect number of arguments.")

	if options.list and options.path:
		parser.error("option -p: only valid when extracting.")

	if options.mkdir and not options.path:
		parser.error("option -m: only valid when --path (-p) is set.")

	if options.list and options.verbose == 0:
		parser.error("option -l: can't be silent while listing data.")

	filename = args[0]

	unarchiver = UnRPA(filename, options.verbose, options.path, options.mkdir, options.version)
	if options.list:
		unarchiver.list_files()
	else:
		unarchiver.extract_files()
