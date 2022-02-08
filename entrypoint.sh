#!/bin/bash

set -e

if [[ "$1" = 'insurance-db' ]]; then
  insurance-db "${@:2}"
fi

if [[ "$1" = '--pdfs_dir' ]]; then
  insurance-db --pdfs_dir "${@:2}"
fi

exec "$@"
