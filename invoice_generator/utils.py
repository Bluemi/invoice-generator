from pathlib import Path
from typing import List, Tuple, TypeVar

from simple_term_menu import TerminalMenu


def get_files(directory: Path) -> List[Path]:
    return [p for p in directory.iterdir() if p.is_file()]


def get_choice_index(title: str, options: List[str], include_cancel: bool = False) -> int:
    if include_cancel:
        options = options + ['cancel']
    menu = TerminalMenu(options, title=title, clear_menu_on_exit=False)
    choice = choice_to_int(menu.show())
    if include_cancel and choice == len(options) - 1:
        raise Cancelled()
    return choice

T = TypeVar('T')

def ask_user(title: str, options: List[T], include_cancel: bool = False) -> T:
    choice = get_choice_index(title, [str(o) for o in options], include_cancel)
    return options[choice]


def choice_to_int(choice: int | Tuple[int, ...] | None) -> int:
    if isinstance(choice, int):
        return choice
    raise Exception('menu entry is tuple')


class Cancelled(Exception):
    def __init__(self, message: str = 'Cancelled'):
        super().__init__(message)
