# mkdocstrings-python-generator

mkdocstrings-python-generator is a mkdocs plugin for generating markdown pages automatically from python source code.

It is intended to fill a gap which is currently left to each user of mkdoctstings-python.  Namely: generating markdown
files for each python file.

_Note despite the name there is no affiliation between mkdocstrings and mkdocstrings-python-generator. Please try to 
determine which plugin is to blame before posting issues here or [there](https://github.com/mkdocstrings/python)._


## Features

Its advantages over the [mkdocstrings-python recipe](https://mkdocstrings.github.io/recipes/#automatic-code-reference-pages) are:

 - ✅ Easier to use (no writing code for yourself)
 - ✅ Well formatted nav out of the box. Package names with underscores are not title case 📦
 - ✅ Compatibility with both explicit nav defined in mkdocs.yaml and implicit nav with no definition in mkdocs.yaml
 - ✅ Supports `__init__.py` files as [section indexes](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/#section-index-pages) if supported by the theme.
 - ✅ Edit URI compatible with both `edit_uri` and `edit_uri_template`

## Minimal Example

See [Configuration](../configuration/) for more detail


```yaml
# Configure mkdocstrings-python
- mkdocstrings:
    handlers:
      python:
        options:
          show_submodules: false

# Configure mkdocstrings-python-generator
- mkdocstrings-python-generator:
    source_dirs:
      # Path to your source directory relative to mkdocs.yaml directory.
      - base: src/
```