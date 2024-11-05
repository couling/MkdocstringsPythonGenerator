# Configuration

## Full Example

For mkdocstrings-python configuration: [see here](https://mkdocstrings.github.io/python/usage/)

```yaml

- mkdocstrings-python-generator:
    source_dirs:
      - nav_heading: ["Code Reference"]
        package_dir: src/my_namespace/my_package
        base: src
        ignore:
          - test_*
        edit_uri: edit/main/src/
        # edit_uri_template: edit/main/src/{path}
        hide_namespace: my_namespace
      
      - ...

# This part of the config is up to you.
- mkdocstrings:
    handlers:
      python:
        ...
```

## Options

| Option Name         | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Value Type      |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|
| `nav_heading`       | Describes where to place the generated files on the nav. Eg: if you want `Reference` > `Code Reference` then set `["Reference", "Code Reference"]`                                                                                                                                                                                                                                                                                                                                                                    | List of Strings |
| `base`              | The source directory of your project relative to the mkdocs configuration yaml file                                                                                                                                                                                                                                                                                                                                                                                                                                   | String          |
| `package_dir`       | Normally `base` is enough, `package_dir` lets you specify exactly which package inside `base` to document.                                                                                                                                                                                                                                                                                                                                                                                                            | Sting           |
| `ignore`            | List of [glob expressions](https://docs.python.org/3/library/glob.html#glob.glob) to ignore from the search. These are applied per file and so cannot specify directories. Default [`test`, `tests`, `__main__.py`].                                                                                                                                                                                                                                                                                                  | List of Strings |
| `edit_uri`          | Override mkdocs [edit_uri](https://www.mkdocs.org/user-guide/configuration/#edit_uri) for generated files                                                                                                                                                                                                                                                                                                                                                                                                             | String          |
| `edit_uri_template` | Override mkdocs [edit_uri_template](https://www.mkdocs.org/user-guide/configuration/#edit_uri_template) for generated files                                                                                                                                                                                                                                                                                                                                                                                           | String          |
| `hide_namespace`    | When using [namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/), it is sometimes unhelpful to have the namespace appear as a level on the nav bar. This option lets you move a namespace's packages up a level and so hide the naspace on the nav.  Simply name the python prefix you want to prune from the nav. Eg: if your package is `foo.bar.my_package` and `foo` is the namespace. Set `hide_namespace: foo` and the nav will then just be `bar` -> `my_package`. | String          |
