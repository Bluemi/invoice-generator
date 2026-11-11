import datetime
import re
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List

import yaml

from invoice_generator.latex import latex_escape
from invoice_generator.utils import get_files, ask_user, format_path, format_date, format_date_opt, parse_date, \
    list_dates, format_price, Cancelled, get_choice_index, parse_price, is_valid_filename

LATEX_LINE_FORMAT = '''{index}. & {description} & {count} & {price} & {price_total} \\\\
\\midrule[\\heavyrulewidth]
'''

@dataclass
class ServiceData:
    index: int
    description: str
    count: int
    price_cents: int | None

    def to_latex_line(self) -> str:
        if self.price_cents is None:
            raise ValueError('Cannot convert to latex line, if price is None')
        return LATEX_LINE_FORMAT.format(
            index=self.index+1, description=latex_escape(self.description), count=self.count,
            price=format_price(self.price_cents), price_total=format_price(self.price_cents * self.count)
        )


@dataclass
class InvoiceData:
    name: str
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
    recp_customer_nr: str = ''
    invoice_nr: str = ''
    invoice_date: Optional[datetime.date] = None
    service_start_date: Optional[datetime.date] = None
    service_end_date: Optional[datetime.date] = None
    services: List[ServiceData] = field(default_factory=list)

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
        latex_body = insert_x(latex_body, self.recp_customer_nr, '__RECP_CUSTOMER_NR__')
        latex_body = insert_x(latex_body, self.invoice_nr, '__INVOICE_NR__')
        latex_body = insert_x(latex_body, format_date_opt(self.invoice_date), '__INVOICE_DATE__')
        latex_body = insert_x(latex_body, self.format_service_time_period(), '__SERVICE_TIME_PERIOD__')
        latex_body = insert_x(latex_body, self.format_services(), '__SERVICES__')
        latex_body = insert_x(latex_body, format_price(self.price_total()), '__SUM_NETTO__')
        latex_body = insert_x(latex_body, format_price(self.price_total()), '__SUM_TOTAL__')
        return latex_body

    def format_service_time_period(self) -> Optional[str]:
        if self.service_start_date is None:
            return None
        if self.service_end_date is None or self.service_end_date == self.service_start_date:
           return f'Lieferdatum & {format_date(self.service_start_date)}'
        if self.service_end_date:
            return f'Leistungszeitraum & {format_date(self.service_start_date)} -- \\ {format_date(self.service_end_date)}'
        raise Exception('This should never happen')

    def format_services(self) -> str:
        lines = [s.to_latex_line() for s in self.services]
        return '\n'.join(lines)

    def price_total(self) -> int:
        price_total = 0
        for s in self.services:
            if s.price_cents is None:
                raise ValueError('Cannot calculate price total, if price_cents is None')
            price_total += s.price_cents * s.count
        return price_total

    def get_output_path(self, extension: str) -> Path:
        if self.invoice_date is None:
            raise ValueError('invoice_date not provided')
        return Path('output') / f'{self.invoice_date.strftime("%Y_%m_%d")}_{self.name}.{extension}'


def insert_x(latex_body: str, value: str | None, latex_key: str) -> str:
    if value:
        latex_body = latex_body.replace(latex_key, value)
    elif latex_key in latex_body:
        raise ValueError(f'key {latex_key} not provided')
    return latex_body


def ask_name() -> str:
    while True:
        print('Invoice name:')
        name = input('> ')
        if is_valid_filename(name):
            return name
        print('Invalid name. Should not contain spaces or special characters.')


def choose_template() -> Path:
    latex_files = get_files(Path('latex'))
    return ask_user('Select a template', latex_files, include_cancel=True, str_convert=format_path)


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
    invoice_data.recp_customer_nr = data['customer_nr']


def normalize_invoice_number(invoice_number: str, invoice_date: datetime.date) -> str:
    cleaned = invoice_number.strip()

    # If already in the format NNNN/YYYY, return as-is
    if re.fullmatch(r"\d{4}/\d{4}", cleaned):
        return cleaned

    # Extract digits and format as 4-digit zero-padded number + /YYYY
    if cleaned.isdigit():
        return f"{int(cleaned):04d}/{invoice_date.year}"

    raise ValueError(f"Invalid invoice number format: {invoice_number}")


def insert_invoice_data(invoice_data: InvoiceData):
    invoice_nr = input('Enter invoice number: ')
    today = datetime.date.today()
    invoice_data.invoice_date = ask_user(
        'Enter invoice date', list_dates(today, 1, 1), include_cancel=True, str_convert=format_date,
        other_convert=parse_date
    )
    invoice_data.service_start_date = ask_user(
        'Enter service start date', list_dates(today, 7, 0), include_cancel=True,
        str_convert=format_date, other_convert=parse_date
    )
    invoice_data.service_end_date = ask_user(
        'Enter service end date', list_dates(invoice_data.service_start_date or today, 0, 2),
        include_cancel=True, str_convert=format_date, other_convert=parse_date
    )
    assert invoice_data.invoice_date is not None
    invoice_data.invoice_nr = normalize_invoice_number(invoice_nr, invoice_data.invoice_date)


def insert_services(invoice_data: InvoiceData):
    services = []
    service_index = 0
    while True:
        service = ask_next_service()
        if service is None:
            break
        service.index = service_index
        service_index += 1
        service.count = ask_count()
        fill_description(service)
        fill_price(service)
        services.append(service)
    invoice_data.services = services


def ask_count() -> int:
    while True:
        try:
            print('Count:')
            count = input('> ')
            return int(count)
        except ValueError:
            continue
    return -1


def fill_description(service: ServiceData):
    formatter = string.Formatter()
    values = []
    index = 1
    explained = False
    try:
        for _, field_name, _, _ in formatter.parse(service.description):
            if field_name is not None:
                if not explained:
                    print('Description contains placeholders:')
                    print(service.description)
                    explained = True
                values.append(latex_escape(input(f'{index}> ')))
                index += 1
    except ValueError:
        # Handles malformed braces like "Hello {"
        print(f'Description is malformed:\n{service.description}')
        return
    service.description = service.description.format(*values)


def fill_price(service: ServiceData):
    if service.price_cents is None:
        service.price_cents = ask_price(True)


def ask_next_service() -> ServiceData | None:
    service_paths = get_files(Path('data/services'))
    options = ['[n] new'] + [str(path) for path in service_paths]
    try:
        choice_index = get_choice_index(
            'What service to add?', options, include_cancel=True, single_auto=False
        )
    except Cancelled:
        return None
    if choice_index == 0:
        return create_new_service()
    service_path = service_paths[choice_index - 1]
    with open(service_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return ServiceData(
        index=-1,
        description=data['description'],
        price_cents=data['price_cents'],
        count=-1
    )


def create_new_service() -> ServiceData:
    while True:
        print('Service name:')
        name = input('> ')
        if name.isidentifier():
            output_path = Path('data/services') / f'{name}.yaml'
            if output_path.exists():
                print(f'Service "{name}" already exists, try again!')
            else:
                break
        else:
            print('Invalid service name, try again!')

    print('Service description:')
    description = input('> ')
    print('Type the price:')
    print('Examples: 1.000,00€   25,50€   0,99€   1.234.567,89€')
    print('Type nothing for a variable price')
    price_cents = ask_price()
    data = ServiceData(-1, description=description, count=-1, price_cents=price_cents)

    # save data
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump({
            'description': description,
            'price_cents': price_cents
        }, f)
    return data


def ask_price(force_value: bool = False) -> int | None:
    while True:
        try:
            price_input = input('> ')
            if price_input == '' and not force_value:
                return None
            return parse_price(price_input)
        except ValueError:
            print('Invalid price, try again:')
