#!/usr/bin/env bash

yesterday=$(date -d "yesterday" '+%Y/%m/%d')
#echo "yesterday"
#echo ${yesterday}

nohup python3 /home/sphinxuser/cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -j 8 -c /home/sphinxuser/cmu-sphinx-decoder/conf/config_ar.ini -i /storage/recordings/2713/${yesterday}  -o decoder_out/ > /home/sphinxuser/logs/${yesterday}.log 2>&1