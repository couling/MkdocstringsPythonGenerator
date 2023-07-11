import logging
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Iterable, List, NamedTuple, Optional, Tuple
from tempfile import TemporaryDirectory
from mkdocs.structure.files import File

log = logging.getLogger(__name__)

ModuleId = Tuple[str, ...]
"""Module Identifier

The module ``foo.bar.baz`` will have id ``("foo", "bar", "baz")``"""


class FileEntry(NamedTuple):
    source_file_path: Path
    doc_file_path: Path
    module_id: ModuleId
    file: File


class Source(NamedTuple):
    base_path: Path
    dir_path: Path
    ignore: List[str]


class FilesGenerator:
    """
    Generates files with all necessary metadata for mkdocs and populating nav elsewhere
    """
    generated_pages: Dict[Path, FileEntry]
    base_path: Path
    _temp_dir: TemporaryDirectory

    def __init__(self, dest_dir: str, use_directory_urls: bool):
        """
        :param dest_dir: Configured mkdocs destination directory
        :param use_directory_urls: Configured mkdocs use_directory_urls
        """
        self.generated_pages = {}
        self._temp_dir = TemporaryDirectory()
        self.base_path = Path(self._temp_dir.name)

        self._dest_dir = dest_dir
        self._use_directory_urls = use_directory_urls

    def cleanup(self) -> None:
        """
        Destroy all local resources including generated pages
        """
        self._temp_dir.cleanup()
        self.generated_pages = {}

    def generate_page(self, source_base_path: Path, source_path: Path, page_template: str) -> FileEntry:
        """
        Generate a markdown page for a given source file.

        Leave a reference for the page in self.generated_pages

        :param source_base_path: Base directory of python files used to determine the full module name
        :param source_path: Python source file path
        :param page_template: Python text template to generate the page
        :return: A ``FileEntry``
        """
        log.debug("Processing %s", source_path)
        module_id = get_module_id(module_path=source_path, base_path=source_base_path)

        target_path = self.file_path_for_module_id(module_id)
        log.debug("Generating %s", target_path)
        target_path.parent.mkdir(exist_ok=True, parents=True)
        with open(target_path, "xt", encoding="utf8") as page:
            page.write(
                page_template.format(
                    module_name=module_id[-1],
                    printable_module_id=module_name(module_id),
                    module_id=module_name(module_id),
                )
            )

        entry = FileEntry(
            source_file_path=source_path,
            doc_file_path=target_path,
            module_id=module_id,
            file=File(
                str(target_path.relative_to(self.base_path)),
                src_dir=str(self.base_path),
                dest_dir=self._dest_dir,
                use_directory_urls=self._use_directory_urls,
            )
        )
        self.generated_pages[entry.doc_file_path.absolute()] = entry
        return entry

    def generate_pages_recursive(self, source: Source, template: str) -> List[FileEntry]:
        """
        Generate pages recursively.

        This will leave references in self.generated_pages as well as returning them as a list

        :param source: source to search through
        :param template: Template to use to generate markdown file
        :return: List of files generated
        """
        entries = []
        for source_file_path in discover_python_files(source.dir_path, source.ignore):
            entry = self.generate_page(
                source_base_path=source.base_path,
                source_path=source_file_path,
                page_template=template,
            )
            entries.append(entry)
        return entries

    def file_path_for_module_id(self, module_id: ModuleId) -> Path:
        if module_id[-1] == "__init__":
            module_id = module_id[:-1] + ("README.md",)
        return Path(self.base_path, "_ref", *module_id).with_suffix(".md")


def get_module_id(module_path: Path, base_path: Path) -> ModuleId:
    """
    Get a module_id for a given file path

    :param module_path: python file path
    :param base_path: the path of the base directory for this package tree.
    """
    return module_path.relative_to(base_path).with_suffix("").parts


def module_name(module_id: ModuleId) -> str:
    """
    Get the module name for a given module_id

    :param module_id: Module ID generated by the function ``module_id()``
    """
    if module_id[-1] == "__init__":
        module_id = module_id[:-1]
    return ".".join(module_id)


def discover_python_files(source_dir: Path, ignore: List[str]) -> Iterable[Path]:
    """
    Discover python files recursively from a directory

    Implicitly skip any ignored files and any empty files. Therefore, this will implicitly skip __init__.py files only
    if they are empty. __main__.py is always ignored.
    """
    for file in sorted(dir for dir in source_dir.iterdir()):
        if any(fnmatch(file.name, pattern) for pattern in ignore):
            continue

        if file.is_dir():
            yield from discover_python_files(file, ignore)

        elif file.is_file() and file.suffix == ".py" and file.name != "__main__.py" and file.read_text().strip():
            yield file