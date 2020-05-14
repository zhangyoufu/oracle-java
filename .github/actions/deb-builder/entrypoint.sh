#!/bin/sh
dpkg-buildpackage "$@"
mv ../*.deb .
