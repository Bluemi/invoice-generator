#!/usr/bin/env python3
from pathlib import Path

from invoice_generator.latex import create_pdf
from invoice_generator.operations import choose_template, insert_logo_path, InvoiceData, insert_recipient_data, \
    insert_personal_data, insert_invoice_data, insert_services


def main():
    template = choose_template()

    with open(template) as f:
        latex_body = f.read()

    invoice_data = InvoiceData()

    insert_logo_path(invoice_data)
    insert_personal_data(invoice_data)
    insert_recipient_data(invoice_data)
    insert_invoice_data(invoice_data)
    insert_services(invoice_data)

    latex_body = invoice_data.apply(latex_body)

    output_path_tex = Path('output/invoice_01.tex')
    output_path_tex.parent.mkdir(exist_ok=True)
    with open(output_path_tex, 'w') as f:
        f.write(latex_body)

    output_path = Path('output/invoice_01.pdf')
    output_path.parent.mkdir(exist_ok=True)
    create_pdf(latex_body, output_path)




if __name__ == '__main__':
    main()

