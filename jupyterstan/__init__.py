import datetime
import humanize
from typing import Tuple, Dict

import argparse

from IPython.core.magic import Magics, cell_magic, magics_class

from IPython.utils.capture import capture_output

import pystan


def parse_args(argstring: str) -> Tuple[str, Dict]:
    # users can separate arguments with commas and/or whitespace
    parser = argparse.ArgumentParser(description="Process pystan arguments.")
    parser.add_argument("variable_name", nargs="?", default="_stan_model")
    parser.add_argument("--model_name")
    parser.add_argument("--include_paths", nargs="*")
    parser.add_argument("--boost_lib")
    parser.add_argument("--eigen_lib")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--obfuscate_model_name", action="store_false")
    kwargs = vars(parser.parse_args(argstring.split()))

    variable_name = kwargs.pop("variable_name")

    if not variable_name.isidentifier():
        raise ValueError(
            f"The variable name {variable_name} is "
            f"not a valid python variable name."
        )

    # set defaults:
    if kwargs["model_name"] is None:
        kwargs["model_name"] = variable_name

    return variable_name, kwargs


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

        variable_name, stan_opts = parse_args(line)

        print(
            f"Creating pystan model & assigning it to variable "
            f'name "{variable_name}".'
        )
        print(f"Stan options:\n", stan_opts)

        start = datetime.datetime.now()
        try:
            with capture_output(display=False) as capture:
                _stan_model = pystan.StanModel(model_code=cell, **stan_opts)
        except Exception:
            print(f"Error creating Stan model:")
            print(capture)
            raise
        end = datetime.datetime.now()
        delta = humanize.naturaldelta(end - start)

        self.shell.user_ns[variable_name] = _stan_model
        print(
            f'StanModel now available as variable "{variable_name}"!\n'
            f"Compilation took {delta}."
        )


def load_ipython_extension(ipython):
    ipython.register_magics(StanMagics)


def unload_ipython_extension(ipython):
    # ipython.user_global_ns.pop('_stan_vars', None)
    pass
