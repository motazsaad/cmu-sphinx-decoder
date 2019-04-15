#!/usr/bin/env bash

channel="2713"

yesterday=$(date -d "yesterday" '+%Y/%m/%d')
#echo "yesterday"
#echo ${yesterday}
yesterday_log=$(date -d "yesterday" '+%Y_%m_%d')

python3 /home/sphinxuser/cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -j 8 -c /home/sphinxuser/cmu-sphinx-decoder/conf/config_ar.ini -i /storage/recordings/${channel}/${yesterday}  -o decoder_out/ &