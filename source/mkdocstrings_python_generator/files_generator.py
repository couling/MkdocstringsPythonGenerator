import logging
from fnmatch import fnmatch
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, List

from mkdocs.structure.files import File

from mkdocstrings_python_generator.config import SourceConfig
from mkdocstrings_python_generator.reference_data import GeneratedFileRef, ModuleRef

log = logging.getLogger(__name__)


class FilesGenerator:
    """
    Generates files with all necessary metadata for mkdocs and populating nav elsewhere
    """
    _temp_dir: TemporaryDirectory

    def __init__(self, dest_dir: str, use_directory_urls: bool):
        """
        :param dest_dir: Configured mkdocs destination directory
        :param use_directory_urls: Configured mkdocs use_directory_urls
        """
        self._temp_dir = TemporaryDirectory()
        self.base_path = Path(self._temp_dir.name)

        self._dest_dir = dest_dir
        self._use_directory_urls = use_directory_urls

    def cleanup(self) -> None:
        """
        Destroy all local resources including generated pages
        """
        self._temp_dir.cleanup()

    def generate_page(self, module_ref: ModuleRef, page_template: str) -> GeneratedFileRef:
        """
        Generate a markdown page for a given source file.

        Leave a reference for the page in self.generated_file

        :param module_ref: Reference to a discovered Module
        :param page_template: Python text template to generate the page
        :return: A ``FileEntry``
        """
        log.debug("Processing %s", module_ref.module_path)

        target_path = self.file_path_for_module_id(module_ref)
        log.debug("Generating %s", target_path)
        target_path.parent.mkdir(exist_ok=True, parents=True)
        with open(target_path, "xt", encoding="utf8") as page:
            page.write(
                page_template.format(
                    module_name=module_ref.module_name,
                    printable_module_id=module_ref.printable_module_id,
                    module_id=module_ref.module_id,
                ))

        entry = GeneratedFileRef(module_ref=module_ref,
                                 doc_file_path=target_path,
                                 file=File(
                                     str(target_path.relative_to(self.base_path)),
                                     src_dir=str(self.base_path),
                                     dest_dir=self._dest_dir,
                                     use_directory_urls=self._use_directory_urls,
                                 ))
        return entry

    def generate_pages_recursive(self, source: SourceConfig, template: str) -> Iterable[GeneratedFileRef]:
        """
        Generate pages recursively.

        This will leave references in self.generated_file as well as returning them as a list

        :param source: source to search through
        :param template: Template to use to generate markdown file
        :return: List of files generated
        """
        base_path = Path(source.base)
        package_dir = Path(source.package_dir or source.base)
        for module_ref in discover_python_files(base_path, package_dir, source.ignore):
            entry = self.generate_page(module_ref=module_ref, page_template=template)
            yield entry

    def file_path_for_module_id(self, module_id: ModuleRef) -> Path:
        """
        Format a .md file path for a file
        :param module_id: The module reference
        :return: An absolute path
        """
        ref_path = module_id.ref_path
        if ref_path[-1] == "__init__":
            ref_path = ref_path[:-1] + ("index.md", )
        elif ref_path[-1].startswith("index"):
            # Move this file to a different name to avoid collision and avoid accidentally making it a section index
            ref_path = ref_path[:-1] + (ref_path[-1] + "_", )
        return Path(self.base_path, "_ref", *ref_path).with_suffix(".md")


def discover_python_files(base_dir: Path, source_dir: Path, ignore: List[str]) -> Iterable[ModuleRef]:
    """
    Discover Python files recursively from a directory

    Implicitly skip any ignored files and any empty files. Therefore, this will implicitly skip __init__.py files only
    if they are empty. __main__.py is always ignored.
    """
    for file in sorted(dir for dir in source_dir.iterdir()):
        if any(fnmatch(file.name, pattern) for pattern in ignore):
            continue

        if file.is_dir():
            yield from discover_python_files(base_dir, file, ignore)

        elif file.is_file() and file.suffix == ".py":
            if not file.read_text().strip():
                log.debug(f"Skipping empty file {str(file)} ")
                continue
            yield ModuleRef(base_dir, file)
