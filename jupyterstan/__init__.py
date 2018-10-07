import re
import json
from typing import Tuple, List, Dict

from IPython.core.magic import Magics, cell_magic, magics_class

from IPython.utils.capture import capture_output

import pystan


def check_program(program):
    """
    Find the path of the given executable.
    """
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return "pystan"


def parse_args(argstring: str) -> Tuple[str, Dict]:
    # users can separate arguments with commas and/or whitespace
    split_pattern = r'(?![^)(]*\([^)(]*?\)\)),\s+(?![^\[]*\])'
    args_kwargs = [arg for arg in re.split(split_pattern, argstring)
                   if len(arg) > 0]
    kwargs = [arg for arg in args_kwargs if '=' in arg]
    args = [arg for arg in args_kwargs if arg not in kwargs]

    if len(args) == 0:
        varname = "_stan_model"
    else:
        varname = args[0]

    kwargs = dict([
        re.split(r'\s*=\s*', kwarg) for kwarg in kwargs
    ])

    # set defaults:
    kwargs['model_name'] = kwargs.get('model_name', varname)
    # the following should be booleans:
    if 'verbose' in kwargs:
        kwargs['verbose'] = kwargs['verbose'] == 'True'
    # the following should be lists:
    for kwarg in ['include_paths', 'extra_compile_args']:
        if kwarg in kwargs:
            kwargs[kwarg] = json.loads(kwargs[kwarg])
            if not isinstance(kwargs[kwarg], list):
                raise TypeError(f"{kwarg} should be a list.")

    return varname, kwargs


@magics_class
class StanMagics(Magics):
    def __init__(self, shell):
        super(StanMagics, self).__init__(shell)

    @cell_magic
    def stan(self, line, cell):
        """
        Allow jupyter notebook cells create a pystan.StanModel object from
        Stan code in a cell that begins with %%stan. The pystan.StanModel
        gets assigned to a variable in the notebook's namespace, either
        named _stan_model (the default), or a custom name (specified
        by writing %%stan <variable_name>).
        """

        varname, stan_opts = parse_args(line)

        if not varname.isidentifier():
            raise ValueError(
                f"The variable name {varname} is not a valid variable name."
            )

        print(
            f"Creating pystan model & assigning it to variable "
            f"name \"{varname}\"."
        )
        print(
            f"Stan options:\n",
            stan_opts
        )

        try:
            with capture_output(display=False) as capture:
                _stan_model = pystan.StanModel(
                    model_code=cell, **stan_opts
                )
        except Exception:
            print(f"Error creating Stan model. Output:")
            print(capture)

        self.shell.user_ns[varname] = _stan_model
        print(f"StanModel now available as variable \"{varname}\"!")


def load_ipython_extension(ipython):
    ipython.register_magics(StanMagics)


def unload_ipython_extension(ipython):
    # ipython.user_global_ns.pop('_stan_vars', None)
    pass
