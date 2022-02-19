#!/bin/bash

set -e

if [[ "$1" = 'insurance-db' ]]; then
  insurance-db "${@:2}"
  exit 1
fi

exec "$@"
