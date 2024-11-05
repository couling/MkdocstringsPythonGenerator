import logging
from collections import deque
from typing import Dict, Iterable, List, Optional, Sequence

from mkdocs.exceptions import PluginError
from mkdocs.structure import StructureItem
from mkdocs.structure.nav import Navigation, Page, Section

from mkdocstrings_python_generator.reference_data import GeneratedFileRef, PageRef

log = logging.getLogger(__name__)


NavPath = Sequence[str]
"""Absolute position of an item in the nav

This is specified as a sequence of Nav Titles from the root to leaf item"""


def get_nav_section(navigation: Navigation, section_path: NavPath) -> list[StructureItem]:
    """Create a section or return an existing one with the same and position in the nav.

    :param navigation: List of children from the nav parent.
    :param section_path: list or tuple of strings listing the section titles in order
    :return: A section defined by section_path
    """
    section_children: List[StructureItem] = navigation.items
    for segment in section_path:
        section_children = _set_default_section(section_children, segment)
    return section_children


def _set_default_section(section_children: List[StructureItem], section_title: str) -> list[StructureItem]:
    """Create a section or return an existing one with the same title.

    :param section_children: List of children from the nav parent.
    :param section_title: The title of the new section
    :return: A section defined by section_title
    """
    for pos, section in enumerate(section_children):
        if section.title == section_title:
            if isinstance(section, Section):
                return section.children
            else:
                raise PluginError(f"mkdocstings-python-generator failed to generate section named '{section_title}':"
                                  f" Something already exists in the nav with this name and is not a Section but a "
                                  f"{type(section).__name__}")

    new_section = Section(title=section_title, children=[])
    section_children.append(new_section)
    return new_section.children


def add_page_to_nav(navigation: Navigation, page_ref: PageRef, nav_path: tuple[str, ...], name_space: tuple[str, ...]) -> None:
    """Add a page into the nav replacing any existing element
    :param navigation: Navigation
    :param page_ref: Page reference including file and module information
    :param name_space: a sequence of strings identifying the relative place in the name to add the page.
        If the page is added for python module foo.bar then the module_id will be ``("foo", "bar")``.
        The page will be added to the nav as <nav_parent> -> "foo" -> "bar".
    :return: The added page.
    """
    page_ref.page.title = page_ref.file.module_ref.module_name
    location = page_ref.file.module_ref.ref_path[:-1]
    if location[:len(name_space)] == name_space:
        location = nav_path + location[len(name_space):]
    else:
        location = nav_path + location
    section_children = get_nav_section(navigation, location)
    section_children.append(page_ref.page)


def patch_nav_refs(nav: Navigation) -> None:
    """Correct the .next, .previous, and .parent refs in the nav

    :param nav: Whole site navigation tree
    """
    stack: deque[StructureItem] = deque()
    stack.extend(nav.items)
    previous: Optional[Page] = None
    while stack:
        item = stack.popleft()
        if isinstance(item, Page):
            item.previous_page = previous
            if previous is not None:
                previous.next_page = item
        elif isinstance(item, Section):
            children = item.children
            if children is not None:
                for child in children:
                    child.parent = item
            stack.extendleft(reversed(item.children))
    if previous is not None:
        previous.next_page = None


def prune_generated_pages(nav_parent: List[StructureItem],
                          generated_files: Dict[str, GeneratedFileRef]) -> Iterable[PageRef]:
    """
    Find generated pages in the nav, remove them and yield them

    Generated pages will be removed from both ``generated_file``, and from ``nav_parent`` or its children.
    :param nav_parent: The .children or .items list of NavItems
    :param generated_files: Dictionary of generated pages with absolute paths pointing to the FileEntry.
    :return: Generator of page items, pages will be removed just before yielding them so will never exist in the nav
        at the moment they are yielded
    """
    for child in list(nav_parent):
        if isinstance(child, Page) and child.file is not None:
            generated_file = generated_files.get(child.file.src_path, None)
            if generated_file is not None:
                nav_parent.remove(child)
                yield PageRef(page=child, file=generated_file)
        elif isinstance(child, Section):
            yield from prune_generated_pages(child.children, generated_files)
            if not (child.is_page or child.children):
                nav_parent.remove(child)
