import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List

import yaml

from invoice_generator.utils import get_files, ask_user, format_path, format_date, format_date_opt, parse_date, \
    list_dates, format_price, Cancelled, get_choice_index, parse_price

LATEX_LINE_FORMAT = '''{index}. & {description} & {count} & {price} & {price_total} \\\\
\\midrule[\\heavyrulewidth]
'''

@dataclass
class ServiceData:
    index: int
    description: str
    count: int
    price_cents: int

    def to_latex_line(self) -> str:
        return LATEX_LINE_FORMAT.format(
            index=self.index+1, description=self.description, count=self.count, price=format_price(self.price_cents),
            price_total=format_price(self.price_cents * self.count)
        )


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


def insert_x(latex_body: str, value: str | None, latex_key: str) -> str:
    if value:
        latex_body = latex_body.replace(latex_key, value)
    elif latex_key in latex_body:
        raise ValueError(f'key {latex_key} not provided')
    return latex_body


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


def insert_invoice_data(invoice_data: InvoiceData):
    invoice_data.invoice_nr = input('Enter invoice number: ')
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
    while True:
        try:
            price_cents = parse_price(input('> '))
            break
        except ValueError:
            print('Invalid price, try again:')
    data = ServiceData(-1, description=description, count=-1, price_cents=price_cents)

    # save data
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump({
            'description': description,
            'price_cents': price_cents
        }, f)
    return data
