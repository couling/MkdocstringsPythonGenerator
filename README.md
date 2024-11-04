# mkdocstrings-python-generator

mkdocstrings-python-generator is a mkdocs plugin for generating markdown pages automatically from python source code.

It is intended to fill a gap which is currently left to each user of mkdoctstings-python.  Namely: generating markdown
files for each python file.

_Note despite the name there is no affiliation between mkdocstrings and mkdocstrings-python-generator. Please try to 
determine which plugin is to blame before posting issues here or [there](https://github.com/mkdocstrings/python)._

## Project Status

This project is in a  very phase of development and not yet recomended for production.

## Running Tests

To run unit tests ensure you have installed the project with all groups (default) or at least `main,dev`.

Run tests with:
```
poetry run pytest
```

## Building the Project

This project uses poetry and poetry-dynamic versioning.

You must either do a full git clone (default) not a shallow one, or you must otherwise ensure git can describe your 
checkout version in terms of tags:

```shell
git describe --tags
```

### Building without using poetry directly

You use a [PEP 517](https://peps.python.org/pep-0517/) build front-end like [build](https://pypi.org/project/build/) 

```shell
python3 -m pip install build
python3 -m build <project dir>
```

### Building via poetry

```shell
poetry self add poetry-dynamic-versioning
cd <project dir>
poetry build
```