"""util functions used to load yaml variables into a python dict."""

import os
import re
from typing import IO, Union

import yaml
from dotenv import load_dotenv

user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, "trekroner.env")
load_dotenv(dotenv_path)


def get_typed_value(value: str) -> Union[float, int, str]:
    """
    Derive true type from data value

    :param value: value

    :returns: value as a native Python data type
    """

    # https://github.com/frafra/pygeoapi/blob/master/pygeoapi/util.py##

    try:
        if "." in value:  # float?
            value2 = float(value)
        elif len(value) > 1 and value.startswith("0"):
            value2 = value
        else:  # int?
            value2 = int(value)
    except ValueError:  # string (default)?
        value2 = value

    return value2


def yaml_load(fh: IO) -> dict:
    """
    serializes a YAML files into a pyyaml object

    :param fh: file handle

    :returns: `dict` representation of YAML
    """

    # support environment variables in config
    # https://stackoverflow.com/a/55301129
    path_matcher = re.compile(r".*\$\{([^}^{]+)\}.*")

    def path_constructor(loader, node):
        env_var = path_matcher.match(node.value).group(1)
        if env_var not in os.environ:
            msg = f"Undefined environment variable {env_var} in config"
            raise EnvironmentError(msg)
        return get_typed_value(os.path.expandvars(node.value))

    class EnvVarLoader(yaml.SafeLoader):
        pass

    EnvVarLoader.add_implicit_resolver("!path", path_matcher, None)
    EnvVarLoader.add_constructor("!path", path_constructor)

    return yaml.load(fh, Loader=EnvVarLoader)
