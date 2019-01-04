# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

readme = open("README.md").read()

setup(
    name="jupyterstan",
    version="0.2.0",
    description="Magics for defining stan code in notebooks.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Jan Freyberg",
    author_email="jan.freyberg@gmail.com",
    url="https://github.com/janfreyberg/jupyterstan",
    packages=find_packages(),
    install_requires=["ipython", "pystan", "humanize"],
    include_package_data=True,
    package_data={
        "stan_syntax": [
            "static/stan_syntax/*.js",
            "static/stan_syntax/*.css",
            "static/stan_syntax/*.yaml",
            "static/stan_syntax/*.md",
        ]
    },
    data_files=[
        ("etc/jupyter/nbconfig/notebook.d/", ["stan_syntax.json"]),
        (
            "share/jupyter/nbextensions/stan_syntax",
            [
                "stan_syntax/static/main.js",
                "stan_syntax/static/stan.js",
                "stan_syntax/static/stan.css",
            ],
        ),
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: IPython",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
