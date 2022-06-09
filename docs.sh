#!/usr/bin/env sh

when-changed -1 -s -r docs/source -c "sphinx-build -ab html docs/source/ docs/build/html"