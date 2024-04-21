#!/usr/bin/env bash
set -ex
exec python -m pytest --junit-xml=junit.xml . --disable-warnings -vv