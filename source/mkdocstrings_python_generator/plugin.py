import logging
from typing import Dict, List

from mkdocs.config import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation, Page

from mkdocstrings_python_generator import files_generator
from mkdocstrings_python_generator.config import GeneratePythonDocsConfig, SourceConfig
from mkdocstrings_python_generator.nav_util import add_page_to_nav, prune_generated_pages, patch_nav_refs
from mkdocstrings_python_generator.reference_data import GeneratedFileRef

log = logging.getLogger(__name__)

MODULE_PAGE = """# `{module_name}`
`{printable_module_id}`

::: {module_id}
"""


class GeneratePythonDocsProcessor:
    _files_generator: files_generator.FilesGenerator
    _generated_files: Dict[str, GeneratedFileRef]
    _namespace: tuple[str, ...] = ()
    _config: SourceConfig

    def __init__(self, source_config: SourceConfig, all_config: MkDocsConfig) -> None:
        self._source_config = source_config
        self._generated_files = {}
        self._files_generator = files_generator.FilesGenerator(
            dest_dir=all_config["site_dir"],
            use_directory_urls=all_config["use_directory_urls"],
        )
        if source_config.hide_namespace:
            self._namespace = tuple(source_config.hide_namespace.split("."))
        self._config = source_config

    def on_files(self, files: Files, config: Config) -> None:
        # Generate all markdown files
        temp_nav_entry = []
        for file_ref in self._files_generator.generate_pages_recursive(self._config, template=MODULE_PAGE):
            self._generated_files[file_ref.file.src_path] = file_ref
            files.append(file_ref.file)
            # This is just a placeholder, don't worry about the title, as long as the src_path is right
            temp_nav_entry.append({file_ref.module_ref.module_id: file_ref.file.src_path})

        if config["nav"] is not None:
            # Stop mkdocs warning that that generated markdown files are not in the nav.
            # Doesn't matter where they go in the nav, it will be fixed later just like auto-generated nav entries
            config["nav"].append({"👻": temp_nav_entry})
        # else:
        # ... Nav entries will be auto-generated.

    def on_pre_page(self, page: Page, *, config: MkDocsConfig) -> None:
        # The markdown file is about to be rendered, this is our oppertunity to set the edit URL so that the link
        # is correctly rendered in HTML.
        src_path = page.file.src_path
        if src_path is not None and (generated_file := self._generated_files.get(src_path, None)) is not None:
            page.edit_url = self.make_edit_url(config, generated_file)

    def on_nav(self, nav: Navigation) -> None:
        # nav items for generated files will almost certainly be in the wrong place...
        # Prune them all
        pages = list(prune_generated_pages(nav.items, self._generated_files))
        pages.sort(key=lambda page: page.file.module_ref.ref_path)

        for page_ref in pages:
            add_page_to_nav(
                navigation=nav,
                page_ref=page_ref,
                nav_path=tuple(self._config.nav_heading),
                name_space=self._namespace,
            )

    def on_shutdown(self) -> None:
        self._cleanup()

    def _cleanup(self):
        self._files_generator.cleanup()
        self._generated_files = {}

    def make_edit_url(self, config: MkDocsConfig, generated_file: GeneratedFileRef) -> str | None:
        # Frustratingly, the mkdocs function to format the edit URL is wrapped up in the constructor of Page
        # Parameters must be supplied through a Config object and a File object.

        # Modify mkdocs config with overrides in this plugin's own configuration
        temp_config = config.copy()
        if self._config.edit_uri is not None or temp_config["edit_uri_template"] is not None:
            # These are supposed to be mutually exclusive, but it's possible the main mkdocs config specifies one
            # and the mkdocstings-python-generator specifies the other.
            temp_config["edit_uri"] = self._config.edit_uri
            temp_config["edit_uri_template"] = self._config.edit_uri_template

        # Make a File object with the python source file as src_uri instead of the .md file
        # This should work on MS Windows
        path = "/".join(generated_file.module_ref.module_path.relative_to(generated_file.module_ref.base_path).parts)
        temp_file = File(
            path=path,
            src_dir="",
            dest_dir=temp_config["site_dir"],
            use_directory_urls=temp_config["use_directory_urls"],
        )
        return Page("👻If you can see this something broke", temp_file, temp_config).edit_url


class GeneratePythonDocs(BasePlugin[GeneratePythonDocsConfig]):
    _source_processors: List[GeneratePythonDocsProcessor]

    def on_config(self, config: MkDocsConfig) -> None:
        self._source_processors = [GeneratePythonDocsProcessor(c, config) for c in self.config.source_dirs]

    def on_files(self, files: Files, config: Config, **kwargs) -> None:
        for processor in self._source_processors:
            processor.on_files(files, config)

    def on_pre_page(self, page: Page, *, config: MkDocsConfig, files: Files) -> None:
        for processor in self._source_processors:
            processor.on_pre_page(page, config=config)

    def on_nav(self, nav: Navigation, *, config: MkDocsConfig, files: Files) -> None:
        for processor in self._source_processors:
            processor.on_nav(nav)
        patch_nav_refs(nav)

    def on_shutdown(self) -> None:
        for processor in self._source_processors:
            processor.on_shutdown()
