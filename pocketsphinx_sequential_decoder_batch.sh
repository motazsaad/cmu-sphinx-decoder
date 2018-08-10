#!/usr/bin/env bash

# sudo apt install pocketsphinx pocketsphinx-en-us
# pocketsphinx_continuous -inmic yes

if [ $# -ne 3 ]; then
    echo "usage ${0} <configuration file> <wave dir> <out>";
    exit -1;
fi

# read cfg file
source ${1}
printf "hmm:%s\n" ${hmm}
printf "lm:%s\n" ${lm}
printf "dict:%s\n" ${dict}


wav_dir=${2}
out_dir=${3}



# a handy SECONDS builtin variable that tracks the number of seconds that have passed since the shell was started.
SECONDS=0

#pocketsphinx_batch -infile ${wav_file} -hmm ${hmm} -lm ${lm} -dict ${dict} -logfn ${log} #> ${out}

pocketsphinx_batch \
 -adcin yes \
 -cepdir ${wav_dir} \
 -cepext .wav \
 -ctl ${wav_dir}.fileids \
 -lm ${lm} \
 -dict ${dict} \
 -hmm ${hmm} \
 -ref ${wav_dir}.ref
 -hyp ${wav_dir}.hyp \
 -logfn ${log}


decode_duration=$SECONDS
echo "total decode time: $(($decode_duration / 60)) minutes and $(($decode_duration % 60)) seconds."

total_duration=0.0
for file in ${wav_dir}/*.wav
do
    duration=$(sox --i -D "$file")
    total_duration=$(python -c "print($total_duration+$duration)")
    s_rate=$(sox --i -r "$file")
    channels=$(sox --i -c "$file")
    filename=$(basename "$file")
    #printf "duration: %s sample rate: %s channels: %d file:%s\n" "$duration" "$s_rate" "$channels" "$filename"
done
printf "total wav duration in minutes: %.2f minutes\n" $(python -c "print($total_duration/60)")
printf "total wav duration in hours: %.2f minutes\n" $(python -c "print($total_duration/60/60)")

decode_duration=$SECONDS
echo "total decode time: $(($decode_duration / 60)) minutes and $(($decode_duration % 60)) seconds."


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


# bash pocketsphinx_sequential_decoder_bash.sh conf/config_ar.cfg ~/wav_files_less_than_1m/ out.txt

