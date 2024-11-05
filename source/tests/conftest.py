import pytest
from pathlib import Path

from mkdocstrings_python_generator.files_generator import FilesGenerator


@pytest.fixture(scope='session')
def example_files() -> Path:
    return Path(__file__).parent / "example"


@pytest.fixture()
def files_generator(tmp_path: Path) -> FilesGenerator:
    generator = FilesGenerator(str(tmp_path / "destination"), use_directory_urls=True)
    yield generator
    generator.cleanup()
