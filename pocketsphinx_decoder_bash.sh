#!/usr/bin/env bash

# sudo apt install pocketsphinx pocketsphinx-en-us
# pocketsphinx_continuous -inmic yes

if [ $# -ne 3 ]; then
    echo "usage ${0} <configuration file> <wave file> <out>";
    exit -1;
fi

# read cfg file
source ${1}
printf "hmm:%s\n" ${hmm}
printf "lm:%s\n" ${lm}
printf "dict:%s\n" ${dict}

wav_file=${2}
printf "wav: %s\n" ${wav_file}

#wav_duration=$(sox --i -D "${wav_file}")
#printf "wav duration: in minutes: %.2f minutes \t in hours: %.2f hours\n" \
#$(python -c "print($wav_duration/60)") $(python -c "print($wav_duration/60/60)")
printf "wave duration: %s\n" $(sox --i ${wav_file} | grep 'Duration' | awk '{print $3}')

out=${3}
printf "out file: %s\n" ${out}
# a handy SECONDS builtin variable that tracks the number of seconds that have passed since the shell was started.
SECONDS=0

# it works fine with en-us model but it does not work with Arabic model.
pocketsphinx_continuous -infile ${wav_file} -hmm ${hmm} -lm ${lm} -dict ${dict}
#-logfn ${log} > ${out}

decode_duration=$SECONDS
echo "$(($decode_duration / 60)) minutes and $(($decode_duration % 60)) seconds elapsed in decoding."






#pocketsphinx_continuous -infile ${1} \
#-hmm ${model} \
#-dict ${dict} \
#-lm ${lm} \
##-beam 1e-50 \
##-ds 2 \
##-topn 3
##-maxwpf 5
##-maxhmmpf 3000
#-backtrace yes \
#-logfn ${log_file} > ${text_out}




