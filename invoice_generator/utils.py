import datetime
# noinspection unused-imports
import readline
from pathlib import Path
import re
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


def format_price(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)

    euros, remainder = divmod(cents, 100)
    # Format whole euros with dots as thousand separators
    formatted_euros = f"{euros:_}".replace("_", ".")

    return f"{sign}{formatted_euros},{remainder:02d}~€"


# Matches strings formatted as [optional -][digits with optional . separators],[exactly 2 digits]€
# Examples: "1.000,00€", "25,50€", "0,99€", "-1.234.567,89€"
PRICE_PATTERN = re.compile(
    r"^(?P<sign>-)?(?P<euros>(?:0|[1-9]\d{0,2}(?:\.\d{3})*)),(?P<cents>\d{2})$"
)

def parse_price(price_str: str) -> int:
    match = PRICE_PATTERN.fullmatch(price_str.strip())
    if not match:
        raise ValueError(f"Invalid price format: {price_str!r}")

    sign = -1 if match.group("sign") else 1
    euros = int(match.group("euros").replace(".", ""))
    cents = int(match.group("cents"))

    return sign * (euros * 100 + cents)


class Cancelled(Exception):
    def __init__(self, message: str = 'Cancelled'):
        super().__init__(message)
