
from common import *


class CompilationBlock:
	def __init__(self, proj, files=False):
		self.project_name = proj.name
		self.out = proj.out_path.add_path("obj")
		self.includes = proj.get_inherited_props("inc_dirs")
		self.definitions = proj.get_inherited_props("definitions")
		self.source_files = []

		if files:
			for file in proj.get_src_files():
				if file.modified:
					self.source_files.append(file)
		else:
			self.source_files = proj.get_src_files()


class PackingBlock:
	def __init__(self, proj):
		self.out = proj.out_path.add_path(proj.name)
		self.from_dir = proj.out_path.add_path("obj")


class LinkingBlock:
	def __init__(self, proj, shared):
		self.out = proj.out_path.add_path(proj.name)
		self.libs = []
		self.lib_dirs = []
		self.shared = shared

		queue = proj.get_build_queue()
		for proj in queue:
			self.lib_dirs.append(proj.out_path)
			self.lib_dirs += proj.external_lib_paths

			self.libs.append(proj.name)
			self.libs += proj.external_lib


class CompileInstructions:
	def __init__(self):
		self.arch = "x64"
		self.platform = "win"
		self.threading = False
		self.debug = False

		self.compile = []
		self.pack = []
		self.link = []

	def pass_console_args(self, csl_args):
		self.arch = csl_args.arch
		self.platform = csl_args.platform
		self.threading = csl_args.threading
		self.debug = csl_args.debug

		self.args = csl_args

	def generate(self, projects, cache_data):

		def get_queue(projs):
			import operator

			def update_levels(proj):
				for dep in proj.dependencies:
					if dep.flag <= proj.flag:
						dep.flag = proj.flag + 1
						update_levels(dep)

			queue = []

			for proj in projs:
				proj.flag = 0

			for proj in projs:
				update_levels(proj)
				queue.append(proj)

			queue.sort(key=operator.attrgetter('flag'))
			return queue

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
