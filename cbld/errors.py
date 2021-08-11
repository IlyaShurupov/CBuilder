
class BuildException(Exception):
    def __init__(self, definition):
        self.definition = definition

    def __str__(self):
        return "Build Error: " + self.definition


class ConfigException(Exception):
    def __init__(self, where, definition):
        self.definition = definition
        self.where = where

    def __str__(self):
        return "Configuration Error: in " + self.where + " - " + self.definition