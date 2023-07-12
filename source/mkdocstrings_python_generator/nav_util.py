import logging
from collections import deque
from pathlib import Path
from typing import Dict, Iterable, List, NamedTuple, Optional, Tuple, Union

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.nav import Link, Navigation, Page, Section

from .files_generator import FileEntry, ModuleId

log = logging.getLogger(__name__)

NavItem = Union[Page, Section, Link]
"""Module Identifier

The module ``foo.bar.baz`` will have id ``("foo", "bar", "baz")``"""


class PageEntry(NamedTuple):
    page: Page
    file: FileEntry


def build_reference_nav(nav: Navigation, generated_pages: Dict[Path, FileEntry], section_heading: List[str],
                        prune_prefix_package: ModuleId, config: MkDocsConfig) -> None:
    """
    [re]build parts of the navigation which were created through dynamic generation
    :param nav: Navigation
    :param generated_pages: generated_pages from files_generator
    :param section_heading: List of titles indicating where to put the generated pages. Eg ``["Reference"]``.
    :param config: MkdocsConfig
    :param prune_prefix_package: Module id to remove if it exists from every pacakge in the nav.
        This is typically useful for pruning namespaces from the nav
    :return:
    """
    generated_pages = generated_pages.copy()

    # Find and move every generated page that is already part of the nav and remove them from their current place
    # The automatically generated nav is usually wrong
    pages_to_add = list(pop_generated_pages(generated_pages, nav.items))
    for file in generated_pages.values():
        page = Page(title="stub", file=file.file, config=config)
        pages_to_add.append(PageEntry(page, file))

    # This ensures the pages are in the right order in the nav
    pages_to_add.sort(key=lambda item: item.file.module_id)

    for page, entry in pages_to_add:
        add_page_to_nav(nav.items, page, nav_path_for_module(section_heading, prune_prefix_package, entry))

    patch_nav_refs(nav)


def nav_path_for_module(section_heading: List[str], prune_prefix_package: ModuleId,
                        entry: FileEntry) -> Tuple[str, ...]:
    """
    Calculate the position of a module in the nav
    :param section_heading: The section heading for reference documentation
    :param prune_prefix_package: Configured prefix to prune from every module
    :param entry: The module's entry
    """
    prefix_length = len(prune_prefix_package)
    if entry.module_id[:prefix_length] == prune_prefix_package:
        module_id = entry.module_id[prefix_length:]
    else:
        module_id = entry.module_id
    return *section_heading, *module_id


def ensure_nav_section(nav_parent: List[NavItem], section_path: Union[List[str], Tuple[str, ...]]) -> Section:
    """Ensure a specific nav section exists and return it

    This will either create the nav section and it's parents or will return the existing one
    :param nav_parent: List of children from the nav parent.
    :param section_path: list or tuple of strings listing the section titles in order
    :return: A section defined by section_path
    """
    for segment in section_path[:-1]:
        nav_parent = ensure_nav_subsection(nav_parent, segment).children
    return ensure_nav_subsection(nav_parent, section_path[-1])


def ensure_nav_subsection(nav_parent: List[NavItem], section_title: str) -> Section:
    """
    Similar to ``ensure_nav_section`` but for one single level.
    :param nav_parent: List of children from the nav parent.
    :param section_title: The title of the new section
    :return: A section defined by section_title
    """
    for section in nav_parent:
        if section.title == section_title:
            if section.children is None:
                section.children = []
            return section
            # TODO check if this section is a page or section_path
    new_section = Section(title=section_title, children=[])
    nav_parent.append(new_section)
    return new_section


def add_page_to_nav(nav_parent: list[NavItem], page: NavItem, module_id: ModuleId) -> None:
    """
    Add a page into the nav replacing any existing element
    :param nav_parent: List .items or .children from the nav section to add the page to
    :param page: Page to add
    :param module_id: sequence of strings identifying the relative place in the name to add the page.
        If the page is added for python module foo.bar then the module_id will be ``("foo", "bar")``.
        The page will be added to the nav as <nav_parent> -> "foo" -> "bar".
    :return: The added page.
    """
    if page.file.src_uri.endswith("README.md"):
        # README.md is optionally used elsewhere for __init__ files to make them a section index page on the nav.
        # Setting the nav title to None indicates this page is the index of the section.
        page.title = None
    else:
        page.title = module_id[-1]
    nav_parent = ensure_nav_section(nav_parent, module_id[:-1]).children

    for item in nav_parent:
        if item.title == page.title:
            nav_parent.remove(item)
            nav_parent.append(page)

            if item.children:
                if page.children is None:
                    page.children = []
                page.children.extend(page.children)
            break
    else:
        nav_parent.append(page)


def patch_nav_refs(nav: Navigation) -> None:
    """
    Correct the .next, .previous, and .parent refs in the nav
    :param nav: Whole site navigation tree
    """
    stack = deque()
    stack.extend(nav.items)
    previous: Optional[Page] = None
    while stack:
        item = stack.popleft()
        if item.is_page:
            item.previous_page = previous
            if previous is not None:
                previous.next_page = item
        if getattr(item, "children", None):
            for child in item.children:
                child.parent = item
            stack.extendleft(reversed(item.children))
    if previous is not None:
        previous.next_page = None


def pop_generated_pages(generated_pages: Dict[Path, FileEntry], nav_parent: List[NavItem]) -> Iterable[PageEntry]:
    """
    Find generated pages in the nav, remove them and yield them

    Generated pages will be removed from both ``generated_pages``, and from ``nav_parent`` or it's children.
    :param generated_pages: Dictionary of generated pages with absolute paths pointing to the FileEntry.
    :param nav_parent: The .children or .items list of NavItems
    :return: Generator or page items, pages will be removed just before yielding them so will never exist in the nav
        at the moment they are yielded
    """
    for child in list(nav_parent):
        if (child_file := getattr(child, "file", None)) is not None:
            if (file_entry := generated_pages.pop(Path(child_file.abs_src_path), None)) is not None:
                nav_parent.remove(child)
                yield PageEntry(child, file_entry)
        if isinstance(getattr(child, "children", None), list):
            yield from pop_generated_pages(generated_pages, child.children)
            if not (child.is_page or child.children):
                nav_parent.remove(child)
