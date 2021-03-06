"""
intercepts setup script
"""
from setuptools import setup, find_packages, Extension

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get version details
version = {}
with open(path.join(here, "intercepts/__version__.py")) as f:
    exec(f.read(), version)

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

builtinhandler_module = Extension(
    "intercepts.builtinhandler", sources=["./intercepts/builtinhandlermodule.c"]
)
builtinutils_module = Extension(
    "intercepts.builtinutils", sources=["./intercepts/builtinutilsmodule.c"]
)

setup(
    name="intercepts",
    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    version=version["__version__"],
    description="Intercept function and method calls",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dlshriver/intercepts",
    author="David Shriver",
    author_email="davidshriver@outlook.com",
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="intercepts testing development",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    project_urls={
        "Source": "https://github.com/dlshriver/intercepts/",
        "Issues": "https://github.com/dlshriver/intercepts/issues",
    },
    ext_modules=[builtinhandler_module, builtinutils_module],
)
