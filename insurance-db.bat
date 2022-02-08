@echo off

SET last=%@:-1%
SET unix_path=`wslpath -ua "%last%"`
IF [[ %last% == --* ]] (
  docker run -it --rm ifrim/insurance-db:ocr-test-7 insurance-db "%@%"
) ELSE (
  docker run -it --rm -v "%last%":"%unix_path%" ifrim/insurance-db:ocr-test-7 insurance-db "%@%"
)