#!/usr/bin/env bash

# sudo apt install pocketsphinx pocketsphinx-en-us
# pocketsphinx_continuous -inmic yes

if [ $# -ne 2 ]; then
    echo "usage ${0} <configuration file> <wave dir>";
    exit -1;
fi

# read cfg file
source ${1}
printf "hmm:%s\n" ${hmm}
printf "lm:%s\n" ${lm}
printf "dict:%s\n" ${dict}


in_dir=${2}

wav_dir=$(echo ${in_dir} | sed "s/\/storage\/recordings\///" | sed "s/\//_/g")

read -p "Convert to wav? " -n 1 -r

if [[ $REPLY =~ ^[Yy]$ ]]
then
##################################################
mkdir -p ${wav_dir}
for f in ${in_dir}/.ts; do file_name=$(basename ${f}); ffmpeg -i ${f} -ar 16000 -ac 1 ~/waves/${wav_dir}/${file_name}.wav; done
printf "%s\n" "conversion to wave format is done"
##################################################
fi

printf "%s\n" "make fileids file (the control file)"
ls -d ${wav_dir}/* | sed -n 's/\.wav//p' > ${wav_dir}.fileid
printf "%s\n" "making fileids file is done"

# a handy SECONDS builtin variable that tracks the number of seconds that have passed since the shell was started.
SECONDS=0

pocketsphinx_batch \
 -adcin yes \
 -cepdir ${wav_dir} \
 -cepext .wav \
 -ctl ${wav_dir}.fileid \
 -lm ${lm} \
 -dict ${dict} \
 -hmm ${hmm} \
 -hyp ${in_dir}_batch.hyp
# -logfn ${log}


echo "done"
decode_duration=$SECONDS
echo "total decode time: $(($decode_duration / 60)) minutes and $(($decode_duration % 60)) seconds."

total_duration=0.0
for file in ${in_dir}/*.wav
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

