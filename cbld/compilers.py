from common import *
import os


class ExceptionBuildError(Exception):
	pass


def paths_to_str(paths):
	out = []
	for path in paths:
		out.append(path.path)
	return out


class Gcc:
	def __init__(self):
		self.name = "gcc"

	def compile_ojs(self, cmpl):
		cmd = "g++ -c  -m" + cmpl.arch.split("x")[1] + " "
		cmd += "  -g " if cmpl.debug else ""

		for cmpl_block in cmpl.compile:

			definitions = to_str(cmpl_block.definitions, 1, " -D\"", 1, "\"")
			includes = to_str(paths_to_str(cmpl_block.includes), 1, " -I\"", 1, "\"")

			if not os.path.isdir(cmpl_block.out.path):
				os.makedirs(os.path.abspath(cmpl_block.out.path))

			for file in cmpl_block.source_files:

				outfile = cmpl_block.out.add_path(file.name).path + ".obj"

				if os.path.isfile(outfile):
					os.remove(outfile)

				print("    [" + cmpl_block.project_name + "]  " + file.name + ".cpp")

				os.system(cmd + file.path.path + definitions + includes + " -o" + outfile)

				if not os.path.isfile(outfile):
					raise ExceptionBuildError

			lib_out = cmpl_block.out.add_path("lib" + cmpl_block.project_name).path + ".a"
			os.system("ar rcs " + lib_out + to_str(paths_to_str(cmpl_block.obj_files), 1, " ", 1, " "))

	def pack_obj(self, cmpl):
		from shutil import copyfile

		cmd = "ar rcs "
		for pack_block in cmpl.pack:

			outfile = pack_block.out.add_path(pack_block.project_name).path + ".a"

			if not os.path.isdir(os.path.dirname(outfile)):
				os.makedirs(os.path.dirname(outfile))

			if os.path.isfile(outfile):
				os.remove(outfile)

			paths = []
			for path in pack_block.lib_files:
				paths.append(path.dir().add_path(path.file_name()).path)

			os.system(cmd + outfile + to_str(paths, 1, " ", 1, ".a "))

			if not os.path.isfile(outfile):
				raise ExceptionBuildError

			headers_dir = pack_block.out.add_path("include")
			if not os.path.isdir(headers_dir.path):
				os.makedirs(os.path.abspath(headers_dir.path))

			for header_file in pack_block.header_files:
				copyfile(header_file.path.path, headers_dir.add_path(header_file.name).path + ".h")

			print("	" + pack_block.out.dir_name() + ".lib")

	def link_libs(self, cmpl):
		cmd = "g++ -static -m" + cmpl.arch.split("x")[1] + " "
		cmd += " -g " if cmpl.debug else ""

		for link_block in cmpl.link:
			print("	" + link_block.out.dir_name() + ".exe")

			outfile = link_block.out.path

			if not os.path.isdir(os.path.dirname(outfile)):
				os.makedirs(os.path.dirname(outfile))

			libs = to_str(link_block.libs, 1, " -l\"", 1, "\"")

			lib_paths = []
			for file in link_block.lib_dirs:
				lib_paths.append(file.path)

			lib_paths = to_str(lib_paths, 1, " -L\"", 1, "\"")

			if os.path.isfile(outfile + ".exe"):
				os.remove(outfile + ".exe")

			print(cmd + lib_paths + libs + " -o " + outfile)
			os.system(cmd + lib_paths + libs + " -o " + outfile)

			if not os.path.isfile(outfile + ".exe"):
				raise ExceptionBuildError

	def compile(self, cmpl, cmd_args, projects):

		print(" ---- Compiling using Gcc ")

		print("Generating objects: ")
		self.compile_ojs(cmpl)

		print("Packing objects into libraries: ")
		self.pack_obj(cmpl)

		print("Linking binaries: ")
		self.link_libs(cmpl)

		print("")


class Msvc:
	def __init__(self):
		self.name = "msvc"
		self.cmpl_path = "D:\\Progs\\windows\\Dev\\VisualStudio\\IDE\\VC\\Tools\\MSVC\\14.28.29910\\bin\\Hostx64\\x64\\"
		self.std_includes = ["D:\\Progs\\windows\\Dev\\VisualStudio\\IDE\\VC\\Tools\\MSVC\\14.28.29910\\include",
							 "G:\\win_progs_backup\\Windows Kits\\10\\Include\\10.0.18362.0\\ucrt"]

	def compile_ojs(self, cmpl):

		cmd = self.cmpl_path + "cl.exe /EHsc "
		cmd += " /Zi " if cmpl.debug else ""

		for cmpl_block in cmpl.compile:

			definitions = "  "  # to_str(cmpl_block.definitions, 1, " -D\"", 1, "\"")
			includes = to_str(paths_to_str(cmpl_block.includes) + self.std_includes, 1, " /I\"", 1, "\"")

			if not os.path.isdir(cmpl_block.out.path):
				os.makedirs(os.path.abspath(cmpl_block.out.path))

			for file in cmpl_block.source_files:

				outfile = cmpl_block.out.add_path(file.name).path + ".obj "

				if os.path.isfile(outfile):
					os.remove(outfile)

				os.system(cmd + " /c " + file.path.path + definitions + includes + " /Fo:" + outfile)

				if not os.path.isfile(outfile):
					raise ExceptionBuildError

	def pack_obj(self, cmpl):
		cmd = self.cmpl_path + "lib.exe "
		for pack_block in cmpl.pack:

			outfile = pack_block.out.path + ".lib "

			if os.path.isfile(outfile):
				os.remove(outfile)

			lib_cmd = cmd + to_str(paths_to_str(GetFiles(pack_block.from_dir, ".obj")), 1, " ", 1, " ") + " /OUT:\"" + outfile
			os.system(lib_cmd)

			if not os.path.isfile(outfile):
				raise ExceptionBuildError

			print("	" + pack_block.out.dir_name() + ".lib")

	def link_libs(self, cmpl):
		cmd = self.cmpl_path + "LINK.exe"
		cmd += " /DEBUG " if cmpl.debug else ""

		for link_block in cmpl.link:
			print("	" + link_block.out.dir_name() + ".exe")

			outfile = link_block.out.path
			libs = " " #to_str(link_block.libs, 1, " -l\"", 1, "\"")

			lib_paths = []
			for file in link_block.lib_dirs:
				lib_paths.append(file.path)

			lib_paths = " " #to_str(lib_paths, 1, " -L\"", 1, "\"")

			if os.path.isfile(outfile + ".exe"):
				os.remove(outfile + ".exe")

			os.system(cmd + lib_paths + libs + " /OUT:\"" + outfile + ".exe\"")

			if not os.path.isfile(outfile + ".exe"):
				raise ExceptionBuildError

	def compile(self, cmpl, cmd_args, projects):
		self.compile_ojs(cmpl)
		self.pack_obj(cmpl)
		self.link_libs(cmpl)
		return

	def __del__(self):
		pass


def perform_compilation(compile_instructions, cmd_args, projects):
	compilers = [Gcc(), Msvc()]

	for compiler in compilers:
		if compiler.name == cmd_args.compiler:
			try:
				compiler.compile(compile_instructions, cmd_args, projects)
				return 0
			except ExceptionBuildError as err:
				print("Compilation terminated because of errors")
	return -1
