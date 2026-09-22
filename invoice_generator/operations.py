from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from invoice_generator.utils import get_files, ask_user

@dataclass
class InvoiceData:
    logo_path: Optional[Path] = None
    firma: str = ''
    website: str = ''
    email: str = ''
    telephone: str = ''
    iban: str = ''
    bic: str = ''
    tax_id: str = ''
    letter_head: str = ''
    recp_person: str = ''
    recp_firma: str = ''
    recp_street: str = ''
    recp_zip_code: str = ''

    def apply(self, latex_body: str) -> str:
        latex_body = insert_x(latex_body, str(self.logo_path.absolute()) if self.logo_path else None, '__LOGO_PATH__')
        latex_body = insert_x(latex_body, self.firma, '__FIRMA__')
        latex_body = insert_x(latex_body, self.website, '__WEBSITE__')
        latex_body = insert_x(latex_body, self.email, '__EMAIL__')
        latex_body = insert_x(latex_body, self.telephone, '__TELEPHONE__')
        latex_body = insert_x(latex_body, self.iban, '__IBAN__')
        latex_body = insert_x(latex_body, self.bic, '__BIC__')
        latex_body = insert_x(latex_body, self.tax_id, '__TAX_ID__')
        latex_body = insert_x(latex_body, self.letter_head, '__LETTER_HEAD__')
        latex_body = insert_x(latex_body, self.recp_person, '__RECP_PERSON__')
        latex_body = insert_x(latex_body, self.recp_firma, '__RECP_FIRMA__')
        latex_body = insert_x(latex_body, self.recp_street, '__RECP_STREET__')
        latex_body = insert_x(latex_body, self.recp_zip_code, '__RECP_ZIP_CODE__')
        return latex_body


def insert_x(latex_body: str, value: str | None, latex_key: str) -> str:
    if value:
        latex_body = latex_body.replace(latex_key, value)
    elif latex_key in latex_body:
        raise ValueError(f'key {latex_key} not provided')
    return latex_body


def choose_template() -> Path:
    latex_files = get_files(Path('latex'))
    return ask_user('Select a template', latex_files, include_cancel=True)


def insert_logo_path(invoice_data: InvoiceData):
    invoice_data.logo_path = ask_user('Select a logo', get_files(Path('logo')), include_cancel=True)


def insert_personal_data(invoice_data: InvoiceData):
    path = ask_user('Personal data', get_files(Path('data/personal_data')), include_cancel=True)

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    invoice_data.firma = data['firma']
    invoice_data.website = data['website']
    invoice_data.email = data['email']
    invoice_data.telephone = data['telephone']
    invoice_data.iban = data['iban']
    invoice_data.bic = data['bic']
    invoice_data.tax_id = data['tax_id']
    invoice_data.letter_head = data['letter_head']


def insert_recipient_data(invoice_data: InvoiceData):
    path = ask_user('Recipient', get_files(Path('data/recipient')), include_cancel=True)

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    invoice_data.recp_person = data['person']
    invoice_data.recp_firma = data['firma']
    if 'firma2' in data:
        invoice_data.recp_firma = f'{invoice_data.recp_firma}\\\\\n{data['firma2']}'
    invoice_data.recp_street = data['street']
    invoice_data.recp_zip_code = data['zip_code']
