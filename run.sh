#!/bin/bash

case "$1" in
	t)
		shift
		pytest "$@"
		;;
	*)
		shift
		.venv/bin/python3 invoice_generator/cli/main.py "$@"
		;;
esac
