#!/usr/bin/env python3
from pathlib import Path

from invoice_generator.latex import create_pdf
from invoice_generator.operations import choose_template, insert_logo_path, InvoiceData


def main():
    template = choose_template()

    with open(template) as f:
        latex_body = f.read()

    invoice_data = InvoiceData()

    # logo
    insert_logo_path(invoice_data)

    latex_body = invoice_data.apply(latex_body)

    output_path = Path('output/invoice_01.pdf')
    output_path.parent.mkdir(exist_ok=True)
    create_pdf(latex_body, output_path)




if __name__ == '__main__':
    main()

