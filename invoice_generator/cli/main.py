#!/usr/bin/env python3
from pathlib import Path

from invoice_generator.utils import get_files, get_choice
from invoice_generator.latex import create_pdf


def main():
    latex_files = get_files(Path('latex'))
    choice = get_choice('Select a template', [str(f) for f in latex_files], include_cancel=True)
    template = latex_files[choice]

    with open(template) as f:
        text = f.read()
        output_path = Path('output/invoice_01.pdf')
        output_path.parent.mkdir(exist_ok=True)
        create_pdf(text, output_path)


if __name__ == '__main__':
    main()

