import logging
from pathlib import Path
from typing import Optional

from mkdocs.config import Config, base, config_options as c
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation, Page

from . import files_generator, nav_util

log = logging.getLogger(__name__)

MODULE_PAGE = """# `{module_name}`
`{printable_module_id}`

::: {module_id}
"""


class GeneratePythonDocsConfig(base.Config):
    nav_heading: list[str] = c.ListOfItems(c.Type(str), default=["Reference"])
    base: str = c.Optional(c.Dir(exists=True))
    search: list[str] = c.ListOfItems(c.Dir(exists=True))
    ignore: list[str] = c.ListOfItems(c.Type(str), default=["test", "tests", "__main__.py"])
    flatten_nav_package: str = c.Type(str, default="")


class GeneratePythonDocs(BasePlugin[GeneratePythonDocsConfig]):
    _files_generator: Optional[files_generator.FilesGenerator] = None

    def on_files(self, files: Files, config: Config, **kwargs):
        self._cleanup()
        self._files_generator = files_generator.FilesGenerator(
            dest_dir=config["site_dir"],
            use_directory_urls=config["use_directory_urls"],
        )
        for search_path in self.config.search:
            self._files_generator.generate_pages_recursive(
                source=files_generator.Source(
                    base_path=Path(self.config.base or search_path),
                    dir_path=Path(search_path),
                    ignore=self.config.ignore,
                ),
                template=MODULE_PAGE,
            )

        for file in self._files_generator.generated_pages.values():
            files.append(file.file)

        if config["nav"] is not None:
            self.patch_config_nav(config)

    def patch_config_nav(self, config: Config) -> None:
        """
        Patches an explicit nave with entries for the generated pages

        The only solid reason for this to exist is to suppress warnings from mkdocs.  Without it, mkdocs would warn that
        generated markdown files were not in the nav.
        """
        dummy_nav_list = [
            {".".join(module.module_id): module.file.src_path}
            for module in self._files_generator.generated_pages.values()
        ]
        config["nav"].append({"_ref": dummy_nav_list})

    def on_page_content(self, html: str, *, page: Page, config: MkDocsConfig, files: Files) -> Optional[str]:
        ...

    def on_nav(self, nav: Navigation, *, config: MkDocsConfig, files: Files) -> None:
        nav_util.build_reference_nav(nav, self._files_generator.generated_pages, self.config.nav_heading, config)

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        self._cleanup()

    def on_shutdown(self) -> None:
        self._cleanup()

    def _cleanup(self):
        if self._files_generator is not None:
            self._files_generator.cleanup()
            self._files_generator = None
