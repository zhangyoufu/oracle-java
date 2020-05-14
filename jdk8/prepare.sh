#!/bin/sh
set -eu

## remove executable permission for shared library / jmc.ini
find . -type f -name '*.so' -perm /111 -exec chmod -x '{}' +
test -x "bin/jmc.ini"
chmod -x "bin/jmc.ini"

## remove non-English manpages
rm -r "man/ja"
rm -r "man/ja_JP.UTF-8"

## remove java-rmi.cgi (deprecated, and hard-coded PATH looks terrible)
rm "bin/java-rmi.cgi"

## remove desktop shortcuts/icons/mime
rm -r "jre/lib/desktop"
rm -r "jre/plugin/desktop"
