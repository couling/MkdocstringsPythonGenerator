from pathlib import Path
from mkdocstrings_python_generator import files_generator


def test_discover_python_files_has_correct_base(example_files: Path):
    assert all(v.base_path == example_files for v in files_generator.discover_python_files(example_files, example_files, []))


def test_discover_correct_module_path(example_files: Path):
    results = {v.module_path for v in  files_generator.discover_python_files(example_files, example_files, [])}
    # Note that sub_package / __init__.py should NOT be present due to being empty.
    assert results == {
        example_files / "foo.py",
        example_files / "bar.py",
        example_files / "__init__.py",
        example_files / "sub_package" / "__main__.py",
        example_files / "sub_package" / "baz.py",
        example_files / "sub_package" / "baz_bob.py",
    }


def test_discover_ignores_files(example_files: Path):
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, [])}
    assert "sub_package.__main__" in results
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, ["__main__.py"])}
    assert "sub_package.__main__" not in results


def test_discover_ignores_wildcard_files(example_files: Path):
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, [])}
    assert "sub_package.baz" in results
    assert "sub_package.baz_bob" in results
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, ["baz*"])}
    assert "sub_package.baz" not in results
    assert "sub_package.baz_bob" not in results


def test_discover_ignores_packages(example_files: Path):
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, [])}
    assert "sub_package.baz" in results
    assert "sub_package.baz_bob" in results
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, ["sub_package"])}
    assert "sub_package.baz" not in results
    assert "sub_package.baz_bob" not in results


def test_non_wildcard_ignore_is_discriminative(example_files: Path):
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, [])}
    assert "sub_package.baz" in results
    assert "sub_package.baz_bob" in results
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, ["baz"])}
    assert "sub_package.baz" in results
    assert "sub_package.baz_bob" in results
    results = {v.module_id for v in files_generator.discover_python_files(example_files, example_files, ["baz.py"])}
    assert "sub_package.baz" not in results
    assert "sub_package.baz_bob" in results


def 