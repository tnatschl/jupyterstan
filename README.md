# jupyterstan

`jupyterstan` is a package to help development of Stan models (using `pystan`)
in jupyter notebooks.

The package is heavily based on Arvinds-ds
[stanmagic](https://github.com/Arvinds-ds/stanmagic) package, but provides an
interface that simply returns a `pystan.Model` object.

In addition, it bundles Arvinds-ds `stan_code_helper` package to improve
syntax highlighting for stan cells.

## Features

- Stan language syntax highlighting in all cells beginning with `%%stan`
- Compile a stan model and save it as a pystan variable by running a `%%stan` cell
- No longer worry about `model_code`, reading in stan files, etc.
- Support for caching compiled stan models: re-executing a cell with the same code will 
  not recompile the code but uses a cached version.

## Installation

To install the library:

```bash
pip install jupyterstan
```

## Usage

To use the `magic` in your notebook, you need to lead the extension:

```python
%load_ext jupyterstan
```

To define a stan model inside a jupyter notebook, start a cell with the `%%stan`
magic. You can also provide a variable name, which is the variable name that
the `pystan.Model` object will be assigned to. For example:

```stan
%%stan paris_female_births
data {
    int male;
    int female;
}

parameters {
    real<lower=0, upper=1> p;
}

model {
    female ~ binomial(male + female, p);
}
```

When you run this cell, `jupyterstan` will create a pystan Model object, which will compile your model and allow
you to sample from it. To use your compiled model:

```python
fit = paris_female_births.sampling(
    data={'male': 251527, 'female': 241945},
    iter=1000,
    chains=4
)
```
