from typing import List, Optional

from mkdocs.config import base, config_options as c


class SourceConfig(base.Config):
    package_dir: Optional[str] = c.Optional(c.Dir(exists=True)) # type: ignore
    ignore: List[str] = c.ListOfItems(c.Type(str), default=["test", "tests", "__main__.py"]) # type: ignore
    base: str = c.Dir(exists=True) # type: ignore
    edit_uri: str = c.Optional(c.Type(str)) # type: ignore
    edit_uri_template: str = c.Optional(c.Type(str)) # type: ignore
    hide_namespace: str = c.Type(str, default="") # type: ignore
    nav_heading: List[str] = c.ListOfItems(c.Type(str), default=["Reference"]) # type: ignore


class GeneratePythonDocsConfig(base.Config):
    source_dirs: List[SourceConfig] = c.ListOfItems(c.SubConfig(SourceConfig)) # type: ignore
