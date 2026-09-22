import datetime
# noinspection unused-imports
import readline
from pathlib import Path
from typing import List, Tuple, TypeVar, Callable, Optional

from simple_term_menu import TerminalMenu


def get_files(directory: Path) -> List[Path]:
    return [p for p in directory.iterdir() if p.is_file()]


T = TypeVar('T')


def ask_user(
        title: str, options: List[T],
        include_cancel: bool = False,
        other_convert: Optional[Callable[[str], T]] = None,
        single_auto: bool = True,
        str_convert: Callable[[T], str] = str
) -> T:
    choice = get_choice_index(
        title, [str_convert(o) for o in options], include_cancel, other_convert is not None, single_auto
    )
    # if other chosen
    if choice == -1:
        return other_convert(input('> '))
    return options[choice]


def get_choice_index(
        title: str,
        options: List[str],
        include_cancel: bool = False,
        include_other: bool = False,
        single_auto: bool = True
) -> int:
    if single_auto and len(options) == 1 and not include_other:
        return 0
    include_other_index = 0
    if include_other:
        options = options + ['[o] other']
        include_other_index = len(options) - 1
    if include_cancel:
        options = options + ['[c] cancel']
    menu = TerminalMenu(options, title=title, clear_menu_on_exit=False)
    choice = choice_to_int(menu.show())
    if include_cancel and choice == len(options) - 1:
        raise Cancelled()
    if include_other and choice == include_other_index:
        return -1
    return choice


def choice_to_int(choice: int | Tuple[int, ...] | None) -> int:
    if isinstance(choice, int):
        return choice
    raise Exception('menu entry is tuple')


def format_date(date: datetime.date) -> str:
    return date.strftime('%d.%m.%Y')


def parse_date(datestr: str) -> datetime.date:
    return datetime.datetime.strptime(datestr, '%d.%m.%Y').date()


def list_dates(
        start: datetime.date = datetime.date.today(),
        past_days: int = 0,
        future_days: int = 0
) -> List[datetime.date]:
    return [start + datetime.timedelta(days=i) for i in range(-past_days, future_days + 1)]


def format_date_opt(date: Optional[datetime.date]) -> Optional[str]:
    return format_date(date) if date is not None else None


def format_path(path: Path) -> str:
    return path.stem


class Cancelled(Exception):
    def __init__(self, message: str = 'Cancelled'):
        super().__init__(message)
