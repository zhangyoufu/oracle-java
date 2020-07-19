#!/bin/sh
set -eu

## remove legal files
rm -r legal/
rm -r jre/legal/

## remove executable permission for shared library
find . -type f -name '*.so' -perm /111 -exec chmod -x '{}' +

## remove non-English manpages
rm -r man/ja
rm -r man/ja_JP.UTF-8

## remove java-rmi.cgi (deprecated, and hard-coded PATH looks terrible)
rm bin/java-rmi.cgi

## remove desktop shortcuts/icons/mime
rm -r jre/lib/desktop
rm -r jre/plugin/desktop

## remove jmc.txt
rm jmc.txt
