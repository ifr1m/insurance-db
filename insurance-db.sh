#!/bin/bash
last=${@:-1}
if [[ -d "$last" ]]; then
  docker run -it --rm -v "$last":"$last" ifrim/insurance-db:0.1.1 insurance-db "${@}"
else
  docker run -it --rm  ifrim/insurance-db:0.1.1 insurance-db "${@}"
fi