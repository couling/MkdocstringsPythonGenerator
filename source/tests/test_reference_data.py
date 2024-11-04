from pathlib import Path

from mkdocstrings_python_generator import reference_data

import pytest


@pytest.mark.parametrize(["file_path", "name"], [
    (("foo", "bar.py"), "bar"),
    (("foo", "__init__.py"), "foo"),
    (("foo", "init.py"), "init"),
])
def test_module_ref_name(file_path: tuple[str, ...], name: str, tmp_path: Path) -> None:
    base_path = tmp_path
    full_file_path = Path(base_path, *file_path)

    module_reference = reference_data.ModuleRef(base_path, full_file_path)

    assert module_reference.module_name == name


@pytest.mark.parametrize(["file_path", "module_id"], [
    (("foo", "bar.py"), "foo.bar"),
    (("foo", "__init__.py"), "foo.__init__"),
    (("foo", "init.py"), "foo.init"),
])
def test_module_ref_module_id(file_path: tuple[str, ...], module_id: str, tmp_path: Path) -> None:
    base_path = tmp_path
    full_file_path = Path(base_path, *file_path)

    module_reference = reference_data.ModuleRef(base_path, full_file_path)

    assert module_reference.module_id == module_id


@pytest.mark.parametrize(["file_path", "module_id"], [
    (("foo", "bar.py"), "foo.bar"),
    (("foo", "__init__.py"), "foo"),
    (("foo", "init.py"), "foo.init"),
])
def test_module_ref_printable_module_id(file_path: tuple[str, ...], module_id: str, tmp_path: Path) -> None:
    base_path = tmp_path
    full_file_path = Path(base_path, *file_path)

    module_reference = reference_data.ModuleRef(base_path, full_file_path)

    assert module_reference.printable_module_id == module_id


@pytest.mark.parametrize(["file_path", "ref_path"], [
    (("foo", "bar.py"), ("foo", "bar")),
    (("foo", "__init__.py"), ("foo", "__init__")),
    (("foo", "init.py"), ("foo", "init")),
])
def test_module_ref_ref_path(file_path: tuple[str, ...], ref_path: tuple[str, ...], tmp_path: Path) -> None:
    base_path = tmp_path
    full_file_path = Path(base_path, *file_path)

    module_reference = reference_data.ModuleRef(base_path, full_file_path)

    assert module_reference.ref_path == ref_path


def test_module_ref_module_path_must_be_in_base_path(tmp_path: Path) -> None:
    base_path = tmp_path / "foo"
    module_path = tmp_path / "bar" / "baz.py"
    with pytest.raises(ValueError):
        _ = reference_data.ModuleRef(base_path, module_path)
