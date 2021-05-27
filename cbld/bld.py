from config import *
from common import *
from compilers import perform_compilation
import json
import sys


class Cache:
    def __init__(self, path):
        self.init_data = {"LastRun": 0.0, "DefaultArgs": {"dbg": False}}
        self.data = self.init_data
        self.path = path

        self.read()

    def read(self):
        if not os.path.isdir(self.path.dir().path):
            os.makedirs(self.path.dir().path)

        if os.path.isfile(self.path.path):
            cache_file = open(self.path.path, "r")
            self.data = json.load(cache_file)
            cache_file.close()
            return

        cache_file = open(self.path.path, "a")
        json.dump(self.init_data, cache_file)
        cache_file.close()

    def update(self):

        def get_time():
            time_file = Path()
            time_file.set_current()
            time_file.Set(time_file.add_path(".time"))
            time = 0
            with open(time_file.path, "a") as file:
                time = os.path.getmtime(time_file.path)
            os.remove(time_file.path)
            return time

        cache_file = open(self.path.path, "w+")
        self.data["LastRun"] = get_time()
        json.dump(self.data, cache_file)
        cache_file.close()


class ConsoleArgs:
    def __init__(self, cmd_args):
        self.root = Path()
        self.out = Path()
        self.debug = False
        self.threading = False
        self.compiler = "gcc"
        self.arch = "x64"
        self.platform = "win"
        self.dependency = "tree"

        self.init(cmd_args)

    def init(self, cmd_args):

        def find_arg(name):
            for arg in range(len(cmd_args)):
                if cmd_args[arg].find(name) != -1:
                    return arg
            return -1

        root = find_arg("-D")
        if root != -1:
            self.root.from_str(cmd_args[root].split("-D")[1])
        else:
            self.root.set_current()

        out = find_arg("-O")
        if out != -1:
            self.out.from_str(cmd_args[root].split("-D")[1])
        else:
            self.out.Set(self.root)
            self.out = self.out.add_path("out")

        if find_arg("msvc") != -1:
            self.compiler = "msvc"

        if find_arg("x86") != -1:
            self.arch = "x86"

        if find_arg("dbg") != -1:
            self.debug = True

        if find_arg("all") != -1:
            self.dependency = "all"

        if find_arg("file") != -1:
            self.dependency = "file"

    def explain(self):
        print("Arguments:")
        print("	-D  - root source dir, default is current dir")
        print("	-O  - output dir, default is \"root source dir\"\\build ")
        print("	dbg  - debug mode")
        print("	gcc  - use self compiler")
        print("	msvc  - use self compiler")
        print("	x64 - use self architecture")
        print("	x86 - use self architecture")
        print("\nexample : gcc -D\"C:\\dev\" dbg x64")


class File:
    def __init__(self, path):
        self.modified = True
        self.name = path.file_name()
        self.path = path
        self.type = path.type()


class Project:

    def __init__(self, path, root_path, out_path):
        self.root_path = root_path
        self.out_path = out_path
        self.path = path

        self.name = self.path.dir_name()
        self.type = "lib"
        self.files = []
        self.dependencies = []

        self.definitions = []
        self.inc_dirs = []
        self.external_lib = []
        self.external_lib_paths = []

        self.flag = 0
        self.flag1 = 0
        self.modified = False

        self.initialize()

    def initialize(self):
        # defaults
        self.name = self.path.dir_name()
        self.type = "lib"
        self.files = []
        self.dependencies = []

        self.definitions = []
        self.inc_dirs = []
        self.external_lib = []

        self.external_lib_paths = []

        self.flag = 0
        self.flag1 = 0
        self.modified = False

    def read_settings(self):
        with open(self.path.add_path("cproject.json").path) as proj_file:
            proj_data = json.load(proj_file)

            if "Name" in proj_data:
                self.name = proj_data["Name"]
            if "Type" in proj_data:
                self.type = proj_data["Type"]
            if "Dependencies" in proj_data:
                self.dependencies = proj_data["Dependencies"]
            if "OutputDirectory" in proj_data:
                self.out_path.from_str(proj_data["OutputDirectory"])
            if "Definitions" in proj_data:
                self.definitions = proj_data["Definitions"]
            if "AdditionalIncludePaths" in proj_data:
                self.inc_dirs = proj_data["AdditionalIncludePaths"]
            if "AdditionalLibraries" in proj_data:
                self.external_lib = proj_data["AdditionalLibraries"]
            if "AdditionalLibraryPaths" in proj_data:
                for lib_dir in proj_data["AdditionalLibraryPaths"]:
                    path = Path()
                    path.from_str(lib_dir)
                    self.external_lib_paths.append(path)

        # decode paths
        def decode_path(path):
            right = path.find("}")
            left = path.find("{")

            if right != -1 and left != -1 and right > left:

                if len(path.split('}')[1]):
                    abs_path = Path()
                    abs_path.from_str(path.split('}')[1])

                    root = path.find("Root")
                    out = path.find("Out")

                    if right > root > left:
                        return self.root_path.add(abs_path)
                    elif left < out < right:
                        return self.out_path.add(abs_path)

            abs_path = Path()
            return abs_path.from_str(path)

        for i in range(len(self.inc_dirs)):
            # self.inc_dirs[i] = decode_path(self.inc_dirs[i])
            pass
        for i in range(len(self.external_lib_paths)):
            # self.external_lib[i] = decode_path(self.external_lib[i])
            pass

        self.out_path = self.out_path.add_path(self.name)
        self.inc_dirs.append(self.path.abs())

    def update_files(self, cache):
        file_paths = GetFiles(self.path, ".cpp")
        file_paths += GetFiles(self.path, ".h")

        self.files = []
        for path in file_paths:
            self.files.append(File(path))

        for file in self.files:
            if os.path.getmtime(file.path.path) < cache.data["LastRun"]:
                file.modified = False

    def update(self, cache):
        self.initialize()
        self.read_settings()
        self.update_files(cache)

        for file in self.files:
            if file.modified:
                self.modified = True

    def get_inherited_props(self, attribute):
        props = []
        props += getattr(self, attribute)

        for dep in self.dependencies:
            props += dep.get_inherited_props(attribute)

        return props

    def get_prnts(self, projs):
        prnts = []
        for may_be_prnt in projs:
            for dep in may_be_prnt.dependencies:
                if dep == self:
                    prnts.append(may_be_prnt)
        return prnts

    def get_src_files(self):
        files = []
        for file in self.files:
            if file.type == "cpp":
                files.append(file)
        return files

    def get_all_deps(self):
        deps = []
        for dep in self.dependencies:
            deps.append(dep)
            deps += dep.get_all_deps()
        return deps

    def get_build_queue(self):
        import operator
        deps = self.get_all_deps()
        deps.sort(key=operator.attrgetter('flag'))
        deps.insert(0, self)
        return deps


def bld(cmd_args):
    def apply_inherent_policy(projects):

        def inherent(proj, prnt):

            # inherent from deps
            if len(proj.dependencies) and not proj.flag:
                for dep in proj.dependencies:
                    inherent(dep, proj)

            # append to parent
            if prnt != 0:
                prnt.definitions += proj.definitions
                prnt.inc_dirs += proj.inc_dirs
                prnt.external_lib += proj.external_lib
                prnt.external_lib_paths += proj.external_lib_paths

            proj.flag = 1

        for proj in projects:
            proj.flag = 0
        for proj in projects:
            inherent(proj, 0)

    def get_projects(proj_files, args, cache):

        def resolve_dependencies(projects):
            for project in projects:
                for dep_idx in range(len(project.dependencies)):
                    found = 0
                    for may_be_dep in projects:
                        if may_be_dep.name == project.dependencies[dep_idx]:
                            project.dependencies[dep_idx] = may_be_dep
                            found = 1
                            break

        # throw if not found

        projs = []

        for proj_path in proj_files:
            project = Project(proj_path.dir(), args.root, args.out)
            project.update(cache)
            projs.append(project)

        resolve_dependencies(projs)
        return projs

    # reading cache
    cache = Cache(args.out.add_path("BldCache.json"))

    # reading projects
    projects = get_projects(GetFiles(cmd_args.root, "cproject.json"), cmd_args, cache)

    # making compiling config
    compile_instructions = CompileInstructions()
    compile_instructions.pass_console_args(cmd_args)
    compile_instructions.generate(projects, cache.data)

    if perform_compilation(compile_instructions, args.compiler) == 0:
        # update cache if succeeds
        cache.update()


if sys.argv[1] == "help":
    args = ConsoleArgs(sys.argv)
    args.explain()

else:
    args = ConsoleArgs(sys.argv)
    bld(args)
