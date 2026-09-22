from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from invoice_generator.utils import get_files, ask_user

@dataclass
class InvoiceData:
    logo_path: Optional[Path] = None

    def apply(self, latex_body: str) -> str:
        if self.logo_path:
            logo_path_str = str(self.logo_path.absolute())
            latex_body = latex_body.replace('__LOGO_PATH__', logo_path_str)
        return latex_body


def choose_template() -> Path:
    latex_files = get_files(Path('latex'))
    return ask_user('Select a template', latex_files, include_cancel=True)


def insert_logo_path(invoice_data: InvoiceData):
    invoice_data.logo_path = ask_user('Select a logo', get_files(Path('logo')), include_cancel=True)
