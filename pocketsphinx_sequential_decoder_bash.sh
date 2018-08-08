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

for wav_file in ${wav_dir}/*.wav
do
printf "wav: %s\n" ${wav_file}
printf "wave duration: %s\n" $(sox --i ${wav_file} | grep 'Duration' | awk '{print $3}')
#printf "out file: %s\n" ${out}



# it works fine with en-us model but it does not work with Arabic model.
pocketsphinx_continuous -infile ${wav_file} -hmm ${hmm} -lm ${lm} -dict ${dict} -logfn ${log} #> ${out}

done
decode_duration=$SECONDS
echo "$(($decode_duration / 60)) minutes and $(($decode_duration % 60)) seconds elapsed in decoding."


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
printf "total wav duration in minutes: %.2f minutes" $(python -c "print($total_duration/60)")
printf "total wav duration in hours: %.2f minutes" $(python -c "print($total_duration/60/60)")



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

