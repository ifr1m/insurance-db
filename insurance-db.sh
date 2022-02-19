#!/bin/bash
last=${@:-1}
if [[ -d "$last" ]]; then
  docker run -it --rm -v "$last":"$last" ifrim/insurance-db:ocr-test-8 insurance-db "${@}"
else
  docker run -it --rm  ifrim/insurance-db:ocr-test-8 insurance-db "${@}"
fi