import os


def GetFiles(dir, extention):
	file_paths = []
	for root, dirs, files in os.walk(dir.abs()):
		for file in files:
			if file.endswith(extention):
				filepath = Path()
				filepath.from_str(os.path.join(root, file))
				file_paths.append(filepath)

	return file_paths


def to_str(elements_list, before=False, separator=' ', after=False, after_sep=' '):
	string = ''
	for item in elements_list:
		if before and after:
			string = string + separator + item + after_sep
		else:
			if after:
				string = string + item + after_sep
			if before:
				string = string + separator + item

	return string


class Path:
	def __init__(self, string=None):
		self.path = ""
		self.prnt = False

		if string:
			self.from_str(string)

	def Set(self, path):
		self.path = path.path
		pass

	def abs(self, path=""):
		if self.prnt:
			pass
		path += self.path
		return path

	def rel(self, path):
		pass

	def from_str(self, string):
		self.path = string
		pass

	def dir(self):
		dir = Path()
		if os.path.isdir(self.path): dir.Set(self)
		else: dir.from_str(os.path.dirname(self.path))
		return dir
	
	def dir_name(self):
		return os.path.basename(self.dir().path)

	def add_path(self, str_path):
		out = Path()
		out.from_str(os.path.join(self.path, str_path))
		return out

	def file(self):
		if os.path.isfile(self.path):
			return os.path.basename(self.path)

	def file_name(self):
		return self.file().split(".")[0]

	def type(self):
		if os.path.isfile(self.path):
			return os.path.basename(self.path).split(".")[1]
		elif os.path.isdir(self.path):
			return "dir"
		else:
			return "none"

	def set_current(self):
		self.path = os.path.abspath(os.path.curdir)