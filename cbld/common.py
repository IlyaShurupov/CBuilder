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
	def __init__(this):
		this.path = ""
		this.prnt = False

	def Set(this, path):
		this.path = path.path
		pass

	def abs(this, path=""):
		if this.prnt:
			path += this.prnt_lnk.abs(path)
		
		path += this.path
		return path

	def rel(this, path):
		pass

	def from_str(this, string):
		this.path = string
		pass

	def dir(this):
		dir = Path()
		if os.path.isdir(this.path): dir.Set(this)
		else: dir.from_str(os.path.dirname(this.path))
		return dir
	
	def dir_name(this):
		return os.path.basename(this.dir().path)

	def add_path(this, str_path):
		out = Path()
		out.from_str(os.path.join(this.path, str_path))
		return out

	def file(this):
		if os.path.isfile(this.path):
			return os.path.basename(this.path)

	def file_name(this):
		return this.file().split(".")[0]

	def type(this):
		if os.path.isfile(this.path):
			return os.path.basename(this.path).split(".")[1]
		elif os.path.isdir(this.path):
			return "dir"
		else:
			return "none"

	def set_current(self):
		self.path = os.path.abspath(os.path.curdir)