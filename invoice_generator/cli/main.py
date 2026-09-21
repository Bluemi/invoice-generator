#!/usr/bin/env python3
from pathlib import Path

from invoice_generator.utils import get_files, get_choice


def main():
    latex_files = get_files(Path('latex'))
    choice = get_choice('Select a template', [str(f) for f in latex_files], include_cancel=True)
    template = latex_files[choice]


if __name__ == '__main__':
    main()

