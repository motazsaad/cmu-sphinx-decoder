# cmu-sphinx-decoder
CMU Sphinx decoder 


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

#### -o/--out 
specify the output output directory. A suffix with process id/part id will be added automatically to the file name. 

#### -j/--jobs  
specify the number of jobs (parallel decoders) if j > number of CPUs/Cores then a error message with appear. j should be <= number of CPUs/Cores. This argument provides the user with flexibility to control the load on the machine. 

#### -l/--log 
enable logging (for debugging purposes)

### example command 
```
python cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -j 8 -c cmu-sphinx-decoder/conf/config_ar.ini -i /storage/recordings/2713/2018/08/16  -o decoder_out/
nohup python cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -j 8 -c cmu-sphinx-decoder/conf/config_ar.ini -i /storage/recordings/2713/2018/08/16 -o decoder_out/ &    
python cmu-sphinx-decoder/pocketsphinx_sequential_decoder.py -c cmu-sphinx-decoder/conf/config_ar.ini -i /storage/recordings/2713/2018/08/16  -o decoder_out/
```

## Error codes:
-1 : config file doest not exisit

-2 : HMM file doesn not exisit

-3 : language model file doesn not exisit

-4 : dictionary file doesn not exisit