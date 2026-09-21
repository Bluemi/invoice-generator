#!/bin/bash

case "$1" in
	r)
		shift
		python3 invoice-generator/cli/main.py "$@"
		;;
	t)
		shift
		pytest "$@"
		;;
	*)
		shift
		echo "invalid option: $@"
esac
