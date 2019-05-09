import argparse
import datetime
import inspect
import os
import pickle
import re
from hashlib import sha256
from pathlib import Path
from typing import Tuple, Dict

import humanize
import pystan
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.utils.capture import capture_output
import shutil


class StanModelCacheClass(object):
    def __init__(self):
        self.cache_path = os.path.join(Path.home(), '.cache', 'stan')
        os.makedirs(self.cache_path, exist_ok=True)

    @classmethod
    def compile_and_store(cls, model_code, model_name, cache_fn, **kwargs):
        sm = pystan.StanModel(model_code=model_code, model_name=model_name, **kwargs)
        with open(cache_fn, 'wb') as f:
            pickle.dump(sm, f)
        return sm

    def get_or_create(self, model_code, cache_file_name=None, recompile=False, model_name=None, **kwargs):
        """Use just as you would `stan`"""

        cache_file_name = cache_file_name or 'model-{digest}.pkl'
        normalized_code = re.sub(r'\s+', ' ', model_code).strip().encode('ascii')
        hasher = sha256(normalized_code)
        hasher.update(repr(kwargs).encode('ascii'))
        digest = hasher.hexdigest()

        cache_fn = cache_file_name.format(digest=digest, model_name=kwargs.get('model_name'))
        cache_fn = os.path.join(self.cache_path, cache_fn)

        if recompile:
            sm = self.compile_and_store(model_code, model_name, cache_fn, **kwargs)
            created = True
        else:
            try:
                sm = pickle.load(open(cache_fn, 'rb'))
            except Exception as e:
                if not isinstance(e, FileNotFoundError):
                    pystan.logger.warning("Problems loading cached model. Recompiling.")
                sm = self.compile_and_store(model_code, model_name, cache_fn, **kwargs)
                created = True
            else:
                pystan.logger.debug("Using cached StanModel '{}'".format(cache_fn))
                created = False

        return sm, created

    def clean(self):
        shutil.rmtree(self.cache_path)
        os.makedirs(self.cache_path, exist_ok=True)


StanModelCache = StanModelCacheClass()


def parse_args(argstring: str) -> Tuple[str, Dict]:
    # users can separate arguments with commas and/or whitespace
    parser = argparse.ArgumentParser(description="Process pystan arguments.")

    parser.add_argument("variable_name", nargs="?", default="_stan_model")
    signature = inspect.signature(pystan.StanModel)

    for arg in ('model_name', 'stanc_ret', 'boost_lib', 'eigen_lib', 'extra_compile_args', 'include_paths'):
        if arg in signature.parameters:
            parser.add_argument('--{}'.format(arg.replace('_', '-')))

    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--recompile", "-v", action="store_true")

    if 'obfuscate_model_name' in signature.parameters:
        parser.add_argument("--obfuscate-model-name", dest='obfuscate_model_name', action="store_true")
        parser.add_argument("--no-obfuscate-model-name", dest='obfuscate_model_name', action="store_false")

    kwargs = vars(parser.parse_args(argstring.split()))

    variable_name = kwargs.pop("variable_name")

    if not variable_name.isidentifier():
        raise ValueError(f"The variable name {variable_name} is not a valid python variable name.")

    # set defaults:
    if kwargs.get('model_name') is None:
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

        pystan.logger.debug("StanModel options: {!r}".format(stan_opts))

        start = datetime.datetime.now()
        try:
            with capture_output(display=False) as capture:
                stan_model, created = StanModelCache.get_or_create(model_code=cell, **stan_opts)
        except Exception:
            pystan.logger.error("Error creating Stan model: {}".format(capture))
            raise
        end = datetime.datetime.now()
        delta = humanize.naturaldelta(end - start)

        self.shell.user_ns[variable_name] = stan_model
        if created:
            pystan.logger.info(f"StanModel available as '{variable_name}' ({delta} compilation time).")
        else:
            stan_model.model_name = stan_opts.get('model_name')
            pystan.logger.info(f"StanModel available as '{variable_name}' (got from cache).")


def load_ipython_extension(ipython):
    ipython.register_magics(StanMagics)


def unload_ipython_extension(ipython):
    # ipython.user_global_ns.pop('_stan_vars', None)
    pass
