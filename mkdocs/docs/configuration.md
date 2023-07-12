# Configuration

## Full Example

For mkdocstrings-python configuration: [see here](https://mkdocstrings.github.io/python/usage/)

```yaml

- mkdocstrings-python-generator:
    nav_heading:
      - Code Reference
    search:
      - src/my_package
    base: src
    ignore:
      - test_*

    
    edit_uri: edit/main/src/
    init_section_index: true
    prune_nav_prefix: my_package

# This part of the config is up to you.
- mkdocstrings:
    handlers:
      python:
        ...
```

## Options

| Option Name          | Description                                                                                                                                                                                                                                  | Value Type      |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|
| `nav_heading`        | Describes where to place the generated files on the nav. Eg: if you want `Reference` > `Code Reference` then set `["Reference", "Code Reference"]`                                                                                           | List of Strings |
| `search`             | Search paths to look for python files relative to mkdocs.yaml                                                                                                                                                                                | List of Strings |
| `base`               | If different from the search paths, set this to the base directory of python files similar to might be added as `PYTHONPATH`. ⚠️ Only one base may be specified                                                                              | String          |
| `ignore`             | List of [glob expressions](https://docs.python.org/3/library/glob.html#glob.glob) to ignore from the search. These are applied per file and so cannot specify directories.                                                                   | List of Strings |
| `edit_uri`           | Override mkdocs [edit_uri](https://www.mkdocs.org/user-guide/configuration/#edit_uri) for generated files                                                                                                                                    | String          |
| `edit_uri_template`  | Override mkdocs [edit_uri_template](https://www.mkdocs.org/user-guide/configuration/#edit_uri_template) for generated files                                                                                                                  | String          |
| `init_section_index` | Some themes such as Material support [section indexes](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/#section-index-pages). If enabled `__init__.py` files with content will be used to define section index pages | Boolean         |
| `prune_nav_prefix`   | If your package exists deep in some namespace you can remove specific parents from the nav keeping the nav cleaner and simpler.  Simply name the python prefix you want to prune from the nav. Eg: `foo.bar.my_namespace_package`            | String          |
