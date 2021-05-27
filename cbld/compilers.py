from common import *
import os


class ExceptionBuildError(Exception):
	pass


class Gcc:
	def __init__(self):
		self.name = "gcc"

	def compile_ojs(self, cmpl):
		cmd = "g++ -c  -m" + cmpl.arch.split("x")[1] + " "
		cmd += " -g " if cmpl.debug else ""

		for cmpl_block in cmpl.compile:

			print("    " + cmpl_block.project_name + ":")

			definitions = to_str(cmpl_block.definitions, 1, " -D\"", 1, "\"")
			includes = to_str(cmpl_block.includes, 1, " -I\"", 1, "\"")

			if not os.path.isdir(cmpl_block.out.path):
				os.makedirs(os.path.abspath(cmpl_block.out.path))

			for file in cmpl_block.source_files:

				outfile = cmpl_block.out.add_path(file.name).path + ".obj "

				if os.path.isfile(outfile):
					os.remove(outfile)

				print("		" + file.name + ".cpp")

				os.system(cmd + file.path.path + definitions + includes + " -o" + outfile)

				if not os.path.isfile(outfile):
					raise ExceptionBuildError

			print("")

	def pack_obj(self, cmpl):
		cmd = "ar rcs "
		for pack_block in cmpl.pack:
			file_paths = []
			for file in GetFiles(pack_block.from_dir, ".obj"):
				file_paths.append(file.path)

			outfile = pack_block.out.path + ".lib"

			if os.path.isfile(outfile):
				os.remove(outfile)

			os.system(cmd + outfile + to_str(file_paths, 1, " ", 1, " "))

			if not os.path.isfile(outfile):
				raise ExceptionBuildError

			print("	" + pack_block.out.dir_name() + ".lib")

		print("")

	def link_libs(self, cmpl):
		cmd = "g++ -static -m" + cmpl.arch.split("x")[1] + " "
		cmd += " -g " if cmpl.debug else ""

		for link_block in cmpl.link:
			print("	" + link_block.out.dir_name() + ".exe")

			outfile = link_block.out.path
			libs = to_str(link_block.libs, 1, " -l\"", 1, "\"")

			lib_paths = []
			for file in link_block.lib_dirs:
				lib_paths.append(file.path)

			lib_paths = to_str(lib_paths, 1, " -L\"", 1, "\"")

			if os.path.isfile(outfile + ".exe"):
				os.remove(outfile + ".exe")

			os.system(cmd + lib_paths + libs + " -o " + outfile)

			if not os.path.isfile(outfile + ".exe"):
				raise ExceptionBuildError

	def compile(self, cmpl):

		print("\n ---- Building using Gcc ---- \n")

		print("Generating objects: ")
		self.compile_ojs(cmpl)

		print("Packing objects into libraries: ")
		self.pack_obj(cmpl)

		print("Linking binaries: ")
		self.link_libs(cmpl)

		print("\n ---- Build succeeded ---- \n")


class Msvc:
	def __init__(self):
		self.name = "msvc"

	def compile_ojs(self, cmpl):

		cmd_buff = ""

		cmd = "cl /EHsc "
		cmd += " /Zi " if cmpl.debug else ""

		for cmpl_block in cmpl.compile:

			definitions = "  " # to_str(cmpl_block.definitions, 1, " -D\"", 1, "\"")
			includes = to_str(cmpl_block.includes, 1, " /I\"", 1, "\"")

			if not os.path.isdir(cmpl_block.out.path):
				os.makedirs(os.path.abspath(cmpl_block.out.path))

			for file in cmpl_block.source_files:

				outfile = cmpl_block.out.add_path(file.name).path + ".obj "

				if os.path.isfile(outfile):
					os.remove(outfile)

				# cmd_buff += " & " + cmd + " /c " + file.path.path + definitions + includes + " /Fo:" + outfile

				if not os.path.isfile(outfile):
					pass
					# raise ExceptionBuildError

		return cmd_buff

	def pack_obj(self, cmpl):
		pass

	def link_libs(self, cmpl):
		pass

	def compile(self, cmpl):

		print("msvc is not supported yet")
		return

		cmd = self.compile_ojs(cmpl)
		os.system("vcvarsall.bat " + cmpl.arch + cmd)

		self.pack_obj(cmpl)
		self.link_libs(cmpl)
		return

	def __del__(self):
		pass


def perform_compilation(compile_instructions, name):

	compilers = [Gcc(), Msvc()]

	for compiler in compilers:
		if compiler.name == name:
			try:
				compiler.compile(compile_instructions)
				return 0
			except ExceptionBuildError as err:
				print("Compilation terminated because of errors")
	return -1
