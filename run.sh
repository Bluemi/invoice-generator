#!/bin/bash

case "$1" in
	r)
		shift
		python3 invoice_generator/cli/main.py "$@"
		;;
	t)
		shift
		pytest "$@"
		;;
	*)
		shift
		echo "invalid option: $@"
esac
