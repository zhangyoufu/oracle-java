#!/bin/sh
set -eu

## remove legal files
rm -r legal/

## remove unrelated manpages (manpages for Windows-only binaries)
for title in jabswitch jaccessinspector jaccesswalker kinit klist ktab; do
	rm "man/man1/${title}.1"
done
