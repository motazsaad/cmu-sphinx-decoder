# cmu-sphinx-decoder
CMU Sphinx decoder app. This application is just an CLI front-end to CMU sphinx decoder. 


## pocketsphinx_parallel_decoder.py 

Decode audio files in parallel. This command load N decoders that run in parallel, where each one decode audio files sequentially. 

```
usage: pocketsphinx_parallel_decoder.py [-h] -i INDIR -c CONF [-l] [-j JOBS] -o OUT

The following arguments are required: -i/--indir, -c/--conf, -o/--out

```

### Arguments: 

#### -i/--indir
The input audio directory. Accepted formats: any format that ffmpeg supports. If the audio files are not in wave format, the code will convert it on the fly (during running time) to /tmp, then they will be deleted after decoding.

#### -c/--conf 
This argument is for the configuration file (ini). You can specify the path for HMM and LM models as well as the dictionary.   

### example command 
```
python cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -c cmu-sphinx-decoder/conf/config_ar.ini -i ts_recordings/wav/2713_20180814 -l -o ts_recordings/wav/jsc_test_20180714 -j 9
```