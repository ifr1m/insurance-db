#!/bin/bash
last=${@:-1}
if [[ $last == --* ]]
then
  docker run -it --rm ifrim/insurance-db:ocr-test-7 insurance-db "${@}"
else
  docker run -it --rm -v "$last":"$last" ifrim/insurance-db:ocr-test-7 insurance-db "${@}"
fi

