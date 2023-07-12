import logging
from pathlib import Path
from typing import Optional

from mkdocs.config import Config, base, config_options as c
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
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
    edit_uri: str = c.Optional(c.Type(str))
    edit_uri_template: str = c.Optional(c.Type(str))
    search: list[str] = c.ListOfItems(c.Dir(exists=True))
    ignore: list[str] = c.ListOfItems(c.Type(str), default=["test", "tests", "__main__.py"])
    init_section_index: bool = c.Type(bool, default=False)
    prune_nav_prefix: str = c.Type(str, default="")


class GeneratePythonDocs(BasePlugin[GeneratePythonDocsConfig]):
    _files_generator: Optional[files_generator.FilesGenerator] = None

    def on_files(self, files: Files, config: Config, **kwargs):
        self._cleanup()
        self._files_generator = files_generator.FilesGenerator(
            dest_dir=config["site_dir"],
            use_directory_urls=config["use_directory_urls"],
            init_section_index=self.config.init_section_index,
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
        dummy_nav_list = [{
            ".".join(module.module_id): module.file.src_path
        } for module in self._files_generator.generated_pages.values()]
        config["nav"].append({"_ref": dummy_nav_list})

    def on_pre_page(self, page: Page, *, config: MkDocsConfig, files: Files) -> Optional[Page]:
        if (generated_file := self._files_generator.generated_pages.get(Path(page.file.abs_src_path))) is None:
            return
        page.edit_url = self.make_edit_url(config, generated_file)

    def on_nav(self, nav: Navigation, *, config: MkDocsConfig, files: Files) -> None:
        nav_util.build_reference_nav(
            nav=nav,
            generated_pages=self._files_generator.generated_pages,
            section_heading=self.config.nav_heading,
            prune_prefix_package=tuple(self.config.prune_nav_prefix.split(".")),
            config=config,
        )

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        self._cleanup()

    def on_shutdown(self) -> None:
        self._cleanup()

    def _cleanup(self):
        if self._files_generator is not None:
            self._files_generator.cleanup()
            self._files_generator = None

    def make_edit_url(self, config: Config, file: files_generator.FileEntry) -> str:

        # Frustratingly, the mkdocs function to format the edit URL is wrapped up in the constructor of Page
        # It takes config and the File.src_uri as inputs
        # To work around this...

        # Make a dummy config with edit_uri and edit_uri_template replaced with this plugin's config.
        if self.config.edit_uri is not None or self.config.edit_uri_template is not None:
            dummy_config = config.copy()
            dummy_config["edit_uri"] = self.config.edit_uri
            dummy_config["edit_uri_template"] = self.config.edit_uri_template
        else:
            dummy_config = config

        # Make a dummy file with the python source file as src_uri instead of the .md file
        dummy_file = File(
            path=("/".join(file.module_id)) + ".py",
            src_dir="",
            dest_dir=dummy_config["site_dir"],
            use_directory_urls=dummy_config["use_directory_urls"],
        )

        # Make a dummy_page page from the dummy_config and dummy_file
        dummy_page = Page("if you can see this something broke", dummy_file, dummy_config)

        # extract the edit_url
        return dummy_page.edit_url
