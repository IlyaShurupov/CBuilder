from config import *
from errors import *
import json
import sys


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


class Project:

    # all data is static
    def __init__(self, path, root_path, out_path):

        self.name = path.dir_name()
        self.path = path
        self.files = []
        self.cproject_script = None

        # defined in configuration file
        self.type = "lib"
        self.dependencies = []
        self.definitions = []
        self.inc_dirs = []
        self.external_lib = []
        self.external_lib_paths = []

        # cache data
        self.modified = False

        # produced data
        self.out_path = out_path.add_path(self.name)
        self.intermediate_path = out_path.add_path(".intermediate").add_path(self.name)
        self.object_files = []

        # should be removed
        self.root_path = root_path
        self.flag = 0
        self.flag1 = 0

    def update(self, cache):
        self.read_settings(cache)
        self.update_files(cache)

        for file in self.files:
            if file.modified:
                self.modified = True

    def read_settings(self, cache):

        def is_var(string):
            left = string.find("{")
            right = string.find("}")
            if left < right:
                return string.split("{")[1].split("}")[0]
            return None

        with open(self.path.add_path("cproject.json").path) as proj_file:
            proj_data = json.load(proj_file)

            if "Type" in proj_data:
                self.type = proj_data["Type"]
            if "Dependencies" in proj_data:
                self.dependencies = proj_data["Dependencies"]
            if "AdditionalLibraries" in proj_data:
                self.external_lib = proj_data["AdditionalLibraries"]

            if "Definitions" in proj_data:
                definitions = proj_data["Definitions"]
                for definition in definitions:

                    if type(definition) is not str:
                        where = "\"" + self.name + "\" project's config file"
                        raise ConfigException(where, "Definitions must be a string")

                    var_name = is_var(definition)
                    if not var_name:
                        self.definitions.append(definition)
                    else:
                        var = cache.get_var(self.name, var_name)
                        if not var:
                            cache.add_var_template(self.name, var_name, "bool")
                            where = "Cache file \"" + self.name + "\" project's variables"
                            error = "Variable \"" + var_name + "\" is not defined"
                            raise ConfigException(where, error)

                        if var.type is not bool:
                            where = "Cache file variable \"" + var_name + "\" of project \"" + self.name + "\""
                            error = "Definition variable must be a bool"
                            raise ConfigException(where, error)

                        if var.value:
                            self.definitions.append(var.name)

            if "AdditionalIncludePaths" in proj_data:
                includes = proj_data["AdditionalIncludePaths"]
                for include_path in includes:

                    if type(include_path) is not str:
                        where = "\"" + self.name + "\" project's config file"
                        raise ConfigException(where, "Include dirs must be a string")

                    var_name = is_var(include_path)
                    if not var_name:
                        self.inc_dirs.append(Path(include_path))
                    else:
                        var = cache.get_var(self.name, var_name)
                        if not var:
                            where = "Cache file \"" + self.name + "\" project's variables"
                            error = "Variable \"" + var_name + "\" is not defined"
                            cache.add_var_template(self.name, var_name, "str")
                            raise ConfigException(where, error)

                        if var.type is not str:
                            where = "Cache file variable \"" + var_name + "\" of project \"" + self.name + "\""
                            error = "AdditionalIncludePaths variable must be a string"
                            raise ConfigException(where, error)

                        if not var.value:
                            where = "Cache file variable \"" + var_name + "\" of project \"" + self.name + "\""
                            error = "Path is not valid "
                            raise ConfigException(where, error)

                        self.inc_dirs.append(Path(var.value))

            if "AdditionalLibraryPaths" in proj_data:
                lib_paths = proj_data["AdditionalLibraryPaths"]
                for lib_path in lib_paths:

                    if type(lib_path) is not str:
                        where = "\"" + self.name + "\" project's config file"
                        raise ConfigException(where, "Library dir must be a string")

                    var_name = is_var(lib_path)
                    if not var_name:
                        self.definitions.append(Path(lib_path))
                    else:
                        var = cache.get_var(self.name, var_name)
                        if not var:
                            where = "Cache file \"" + self.name + "\" project's variables"
                            error = "Variable \"" + var_name + "\" is not defined"
                            cache.add_var_template(self.name, var_name, "str")
                            raise ConfigException(where, error)

                        if var.type is not str:
                            where = "Cache file variable \"" + var_name + "\" of project \"" + self.name + "\""
                            error = "AdditionalLibraryPaths variable must be a string"
                            raise ConfigException(where, error)

                        if not var.value:
                            where = "Cache file variable \"" + var_name + "\" of project \"" + self.name + "\""
                            error = "Path is not valid "
                            raise ConfigException(where, error)

                        self.external_lib_paths.append(Path(var.value))

        self.inc_dirs.append(self.path)

    def update_files(self, cache):
        file_paths = GetFiles(self.path, ".cpp")
        file_paths += GetFiles(self.path, ".h")

        self.files = []
        for path in file_paths:
            self.files.append(File(path))

        for file in self.files:
            if os.path.getmtime(file.path.path) < cache.data["LastRun"]:
                file.modified = False


    def clear_child_flags(self):
        for dep in self.dependencies:
            dep.clear_child_flags()
            dep.flag = 0

    def inherit_not_repeated(self, attribute):
        props = []
        props += getattr(self, attribute)

        for dep in self.dependencies:
            if dep.flag == 0:
                props += dep.inherit_not_repeated(attribute)
                dep.flag = 1

        return props

    def get_inherited_props(self, attribute):
        self.clear_child_flags()
        return self.inherit_not_repeated(attribute)

    def get_prnts(self, projs):
        prnts = []
        for may_be_prnt in projs:
            for dep in may_be_prnt.dependencies:
                if dep == self:
                    prnts.append(may_be_prnt)
        return prnts

    def get_files(self, file_type):
        files = []
        for file in self.files:
            if file.type == file_type:
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


def link_scripts(projects):
    return
    for project in projects:
        path = project.path.dir().add_path("cproject.py").path
        print(path)
        if os.path.isfile(path):
            sys.path.append(project.path.dir().path)
            project.cproject_script = __import__(path)
            sys.path.remove(project.path.dir().path)


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
                if not found:
                    where = " project \"" + project.name + "\" "
                    raise ConfigException(where, "Dependency \"" + project.dependencies[dep_idx] + "\" not found")

    projs = []

    for proj_path in proj_files:
        project = Project(proj_path.dir(), args.root, args.out)
        project.update(cache)
        projs.append(project)

    resolve_dependencies(projs)
    link_scripts(projs)
    return get_queue(projs)



