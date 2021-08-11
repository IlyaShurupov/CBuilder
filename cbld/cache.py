from common import *
import json


class Var:
    def __init__(self, project, name, value=None):
        self.type = type(value)
        self.name = name
        self.project = project
        self.value = value


class Cache:
    def __init__(self, path, cmd_args):

        self.init_data = {
            "LastRun": 0.0
        }

        self.data = self.init_data
        self.path = path
        self.vars = []

        try:
            self.read()

        except json.decoder.JSONDecodeError as error:
            raise ConfigException("cache file", "json syntax error")

        self.init_vars(cmd_args)

    def init_vars(self, cmd_args):
        if "Variables" in self.data:
            vars = self.data["Variables"]
            for proj_name, proj_vars in vars.items():
                for var_name, value in proj_vars.items():
                    self.vars.append(Var(proj_name, var_name, value))

    def add_var_template(self, project_name, var_name, type):
        with open(self.path.path, "w+") as cnfg_file:
            if "Variables" not in self.data:
                self.data["Variables"] = {}
            if project_name not in self.data["Variables"]:
                self.data["Variables"][project_name] = {}

            self.data["Variables"][project_name][var_name] = ""
            json.dump(self.data, cnfg_file, indent=2)

    def get_var(self, project, var_name):
        for var in self.vars:
            if var.project == project:
                if var.name == var_name:
                    return var
        return None

    def read(self):
        if not os.path.isdir(self.path.dir().path):
            os.makedirs(self.path.dir().path)

        if os.path.isfile(self.path.path):
            cache_file = open(self.path.path, "r")
            self.data = json.load(cache_file)
            cache_file.close()
            return

        cache_file = open(self.path.path, "a")
        json.dump(self.init_data, cache_file, indent=2)
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
        json.dump(self.data, cache_file, indent=2)
        cache_file.close()