
from config import *
from common import *
from errors import *

from cproject import *
from cache import *
from compilers import perform_compilation
import sys


def bld(cmd_args):
    print(" ---- reading solution file")
    solution_files = GetFiles(cmd_args.root, "cbuild.json")
    if len(solution_files) != 1:
        raise ConfigException("working directory", "multiple or no cbuild.json files were found")

    print(" ---- reading cache")
    cache = Cache(cmd_args.out.add_path("BldCache.json"), cmd_args)

    print(" ---- reading projects")
    projects = get_projects(GetFiles(cmd_args.root, "cproject.json"), cmd_args, cache)

    print(" ---- generating compilation instructions")
    compile_instructions = CompileInstructions()
    compile_instructions.pass_console_args(cmd_args)
    compile_instructions.generate(projects, cache.data)

    print(" ---- running prebuild scripts")
    for proj in projects:
        if proj.cproject_script:
            proj.cproject_script.prebuild(proj, cmd_args, cache)

    print(" ---- starting the compilation")
    perform_compilation(compile_instructions, cmd_args, projects)

    print(" ---- running postbuild scripts")
    for proj in projects:
        if proj.cproject_script:
            proj.cproject_script.postbuild(proj, cmd_args, cache)

    print(" ---- updating cache")
    cache.update()


def print_help():
    print("Arguments:")
    print("	-D  - root source dir, default is current dir")
    print("	-O  - output dir, default is \"root source dir\"\\build ")
    print("	dbg  - debug mode")
    print("	gcc  - use self compiler")
    print("	msvc  - use self compiler")
    print("	x64 - use self architecture")
    print("	x86 - use self architecture")
    print("\nexample : gcc -D\"C:\\dev\" dbg x64")


class ConsoleArgs:
    def __init__(self, cmd_args):

        def find_arg(name):
            for arg in range(len(cmd_args)):
                if cmd_args[arg].find(name) != -1:
                    return arg
            return -1

        # init root directory
        root = find_arg("-D")
        if root == -1:
            raise ConfigException("command line arguments", "root directory must be specified")
        self.root = Path(cmd_args[root].split("-D")[1])

        self.compiler = "msvc" if find_arg("msvc") != -1 else "gcc"
        self.arch = "x86" if find_arg("x86") != -1 else "x64"
        self.debug = True if find_arg("debug") != -1 else False

        if find_arg("all") != -1: self.dependency = "all"
        elif find_arg("file") != -1: self.dependency = "all"
        else: self.dependency = "tree"

        # init output directory
        self.out = None
        out = find_arg("-O")
        if out != -1:
            self.out = Path(cmd_args[root].split("-D")[1])
        else:
            self.out = self.root.add_path("out")


def cmd_invoke(cmd_argv):
    if cmd_argv[1] == "help":
        print_help()
        return

    try:
        bld(ConsoleArgs(cmd_argv))
    except (BuildException, ConfigException) as bld_error:
        print(bld_error)


if __name__ == "__main__":
    cmd_invoke(sys.argv)
