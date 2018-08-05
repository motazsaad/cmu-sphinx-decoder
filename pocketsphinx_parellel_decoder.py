"""
This decoder is based on pocketsphinx python package.
url: https://pypi.org/project/pocketsphinx/
to install:
python -m pip install --upgrade pip setuptools wheel
sudo apt install libasound2-dev
pip install --upgrade pocketsphinx
"""

import argparse
import datetime
import glob
import io
import multiprocessing
import os
import sys
import time
import configparser
from multiprocessing.pool import Pool

from pocketsphinx import DefaultConfig, Decoder, get_model_path
from pydub import AudioSegment


def load_decoder(model_config):
    # Create a decoder with certain model
    pocketsphinx_config = DefaultConfig()
    model_name = model_config.sections()[0]
    hmm = model_config[model_name]['hmm']
    dict = model_config[model_name]['dict']
    lm = model_config[model_name]['lm']
    logfn = model_config[model_name]['log']
    print('hmm:', hmm)
    print('lm:', lm)
    print('dict:', dict)
    pocketsphinx_config.set_string('-hmm', hmm)
    pocketsphinx_config.set_string('-lm', lm)
    pocketsphinx_config.set_string('-dict', dict)
    pocketsphinx_config.set_string('-logfn', logfn)
    decoder_engine = Decoder(pocketsphinx_config)
    return decoder_engine


def decode_audio(audio_file):
    decode_result = {}
    audio_segment = AudioSegment.from_file(audio_file)
    # audio_segment = audio_segment.set_frame_rate(16000)
    # audio_segment = audio_segment.set_channels(1)
    duration = audio_segment.duration_seconds
    conversion_time = 0
    if not audio_file.endswith('.wav'):
        conversion_start_time = time.time()
        # print('converting {} to wav'.format(audio_file))
        wav_in_ram = io.BytesIO()
        # data = audio_segment.raw_data
        # wav_in_ram.write(data)
        # wav_in_ram.seek(0)
        audio_segment.export(wav_in_ram, format="wav", parameters=['-ar', '16000', '-ac', '1'])
        wav_in_ram.seek(0)
        wav_stream = wav_in_ram
        conversion_time = time.time() - conversion_start_time
        # print('{} has been converted to wav'.format(audio_file))
    else:
        wav_stream = open(audio_file, 'rb')
    decode_time_start_time = time.time()
    my_decoder.start_utt()
    while True:
        buf = wav_stream.read(1024)
        if buf:
            my_decoder.process_raw(buf, False, False)
        else:
            break
    my_decoder.end_utt()
    hypothesis = my_decoder.hyp()
    try:
        text = hypothesis.hypstr
    except AttributeError:
        text = ''
    decode_time = time.time() - decode_time_start_time
    decode_result[audio_file] = (duration, decode_time, conversion_time, text)
    return decode_result


def split_list(data, n_parts):
    if len(data) <= n_parts:
        return [data]
    else:
        part_size = int(len(data) / n_parts)
        # print('part size {}'.format(part_size))
        parts = [data[x:x + part_size] for x in range(0, len(data), part_size)]
        if len(parts[-1]) < part_size:
            parts[-2].extend(parts[-1])
            del parts[-1]
        return parts


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for j in range(0, len(l), n):
        yield l[j:j + n]


def split_list_on_cpus(data_list, cpus_number):
    list_size = len(data_list)
    if list_size <= cpus_number:
        return [data_list]
    else:
        return list(chunks(data_list, cpus_number))


parser = argparse.ArgumentParser(description='This decoder is based CMU Sphinx (works offline) engine provided by '
                                             'speech_recognition python package.')  # type: ArgumentParser
parser.add_argument('-i', '--indir', type=str,
                    help='input wave directory', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file', required=True)
parser.add_argument('-o', '--outdir', type=str, help='output directory')


if __name__ == '__main__':
    cpu_count = os.cpu_count()
    print('number of CPUs: {}'.format(cpu_count))
    args = parser.parse_args()
    in_dir = args.indir
    audio_files = sorted(glob.glob(os.path.join(in_dir, '*.*')))
    num_files = len(audio_files)
    if num_files == 0:
        print("no files found in {}".format(in_dir))
        sys.exit(-1)
    print('# of audio files: {}'.format(num_files))
    audio_file_lists = split_list_on_cpus(audio_files, cpu_count)
    print('number of parts: {}'.format(len(audio_file_lists)))
    for i, p in enumerate(audio_file_lists):
        print('part {} has {} audio segments'.format(i, len(p)))
    ###################################################
    # load configuration
    config = configparser.ConfigParser()
    conf_file = args.conf
    if not os.path.exists(conf_file):
        print('ERROR: {} doest not exisit'.format(conf_file))
        sys.exit(-1)
    config.read(conf_file)
    print('loading decoder models ...')
    my_decoder = load_decoder(config)
    print('decoder has been loaded ...')
    ###################################################
    # process lists:
    print('processing lists')
    results = {}
    for i, audio_list in enumerate(audio_file_lists):
        print('process {} files in parallel in part {}'.format(len(audio_list), i))
        pool = multiprocessing.Pool(processes=cpu_count)
        result = pool.map(decode_audio, audio_list)
        # print(result)
        for r in result:
            results.update(r)
    ##########################################
    if not args.outdir:
        total_duration = 0
        total_decode_time = 0
        total_conversion_time = 0
        for k, v in results.items():
            print('file: {}'.format(k))
            file_duration, file_decode_time, file_conversion_time, transcription = v
            print('transcription: \n{}'.format(transcription))
            print('duration: {0:.2f}'.format(file_duration))
            print('decode time: {0:.2f}'.format(file_decode_time))
            print('conversion time: {0:.2f}'.format(file_conversion_time))
            print('######################################')
            total_duration += file_duration
            total_decode_time += file_decode_time
            total_conversion_time += file_conversion_time
        print('total audio duration: {}'.format(datetime.timedelta(seconds=total_duration)))
        print('total decode time: {}'.format(datetime.timedelta(seconds=total_decode_time)))
        print('total conversion time: {}'.format(datetime.timedelta(seconds=total_conversion_time)))
    else:
        if not os.path.exists(args.outdir):
            try:
                os.mkdir(args.outdir)
                print('{} created successfully'.format(args.outdir))
            except OSError as error:
                print('Error: {}'.format(error))
                sys.exit(-1)
        for my_file, v in results.items():
            file_duration, file_decode_time, file_conversion_time, transcription = v
            out_file_name, ext = os.path.splitext(os.path.basename(my_file))
            with open(os.path.join(args.outdir, out_file_name + '.txt'), mode='w') as file_writer:
                file_writer.write(transcription)
        print('done!')

"""
How to run: 
python pocketsphinx_parellel_decoder.py -i wav/en -c conf/config_en.ini 
python pocketsphinx_parellel_decoder.py -i wav/ar -c conf/config_ar.ini
python pocketsphinx_parellel_decoder.py -i ~/wav_files_less_than_1m/ -c conf/config_ar.ini
python cmu-sphinx-decoder/pocketsphinx_parellel_decoder.py -i wav_files_less_than_1m/ -c cmu-sphinx-decoder/conf/config_ar.ini
python pocketsphinx_parellel_decoder.py -i ~/ts_sample_files/ -c conf/config_ar.ini

python pocketsphinx_parellel_decoder.py -i ~/PycharmProjects/jsc-news-broadcast/mp3/ -c conf/config_ar.ini


python cmu-sphinx-decoder/pocketsphinx_parellel_decoder.py -i jsc-news-broadcast/wav_split/headlines_10pm_29_07_2017/mp3/ -c cmu-sphinx-decoder/conf/config_ar.ini -o out

"""
