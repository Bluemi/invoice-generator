#!/usr/bin/env python3
from pathlib import Path

from invoice_generator.latex import create_pdf
from invoice_generator.operations import choose_template, insert_logo_path, InvoiceData, insert_recipient_data, \
    insert_personal_data, insert_invoice_data, insert_services, ask_name


def main():
    template = choose_template()

    with open(template) as f:
        latex_body = f.read()

    name = ask_name()
    invoice_data = InvoiceData(name=name)

    insert_logo_path(invoice_data)
    insert_personal_data(invoice_data)
    insert_recipient_data(invoice_data)
    insert_invoice_data(invoice_data)
    insert_services(invoice_data)

    latex_body = invoice_data.apply(latex_body)

    # create output dir
    Path('output').mkdir(exist_ok=True)

    # dump tex
    with open(invoice_data.get_output_path('tex'), 'w') as f:
        f.write(latex_body)

    # dump pdf
    create_pdf(latex_body, invoice_data.get_output_path('pdf'))




if __name__ == '__main__':
    main()

