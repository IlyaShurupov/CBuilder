
from common import *
from cproject import *

class CompilationBlock:
	def __init__(self, proj, files=False):
		self.project_name = proj.name
		self.out = proj.intermediate_path
		self.includes = proj.get_inherited_props("inc_dirs")
		self.definitions = proj.get_inherited_props("definitions")
		self.source_files = []
		self.obj_files = []

		if files:
			for file in proj.get_files("cpp"):
				if file.modified:
					self.source_files.append(file)
		else:
			self.source_files = proj.get_files("cpp")

		obj_file_names = []
		for file in proj.get_files("cpp"):
			obj_file_names.append(file.name + ".obj")

		for file_name in obj_file_names:
			self.obj_files.append(Path(proj.intermediate_path.add_path(file_name).path))


class PackingBlock:
	def __init__(self, proj):
		self.project_name = proj.name
		self.out = proj.out_path
		self.header_files = proj.get_files("h")
		self.lib_files = []

		for proj in proj.get_build_queue():
			self.lib_files.append(proj.intermediate_path.add_path(proj.name + ".a"))


class LinkingBlock:
	def __init__(self, proj, shared):
		self.out = proj.out_path.add_path(proj.name)
		self.libs = []
		self.lib_dirs = []
		self.shared = shared

		queue = proj.get_build_queue()
		for proj in queue:
			self.lib_dirs.append(proj.intermediate_path)
			self.lib_dirs += proj.external_lib_paths

			self.libs.append(proj.name)
			self.libs += proj.external_lib


class CompileInstructions:
	def __init__(self):
		self.arch = "x64"
		self.debug = False
		self.args = None
		self.compile = []
		self.pack = []
		self.link = []

	def pass_console_args(self, csl_args):
		self.arch = csl_args.arch
		self.debug = csl_args.debug
		self.args = csl_args

	def generate(self, projects, cache_data):

		def get_rebuild_queue(queue):
			rebuild_projs = []
			if self.args.dependency == "tree":

				def mark_prnts(proj):
					for prnt in proj.get_prnts(queue):
						prnt.flag1 = 1
						mark_prnts(prnt)

				for proj in queue:
					if proj.modified:
						proj.flag1 = 1
						mark_prnts(proj)

				for proj in queue:
					if proj.flag1:
						rebuild_projs.append(proj)
			else:
				# all
				rebuild_projs = queue
			return rebuild_projs

		def pump_compilation_blocks(reb_queue):
			for reb_proj in reb_queue:
				self.compile.append(CompilationBlock(reb_proj, self.args.dependency == "file"))

		def pump_pack_blocks(reb_queue):
			for proj in reb_queue:
				if proj.type == "StaticLibrary":
					self.pack.append(PackingBlock(proj))

		def pump_link_blocks(reb_queue):
			for reb in reb_queue:
				if reb.type == "exe" or reb.type == "dll":
					self.link.append(LinkingBlock(reb, reb.type == "dll"))

		build_queue = get_queue(projects)
		rebuild_queue = get_rebuild_queue(build_queue)

		pump_compilation_blocks(rebuild_queue)
		pump_pack_blocks(rebuild_queue)
		pump_link_blocks(rebuild_queue)
