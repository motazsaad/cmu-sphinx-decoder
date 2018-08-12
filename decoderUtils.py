import io
import logging
import os
import time
from datetime import timedelta
from pocketsphinx import DefaultConfig, Decoder
from pydub import AudioSegment
from collections import OrderedDict


logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)


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


def decode_audio(audio_file, decoder):
    decode_result = {}
    audio_segment = AudioSegment.from_file(audio_file)
    duration = audio_segment.duration_seconds
    if not audio_file.endswith('.wav'):
        conversion_start_time = time.time()
        logging.info('converting {} to wav'.format(audio_file))
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_segment = audio_segment.set_channels(1)
        tmp_file_name = '/tmp/' + os.path.basename(audio_file) + '.wav'
        audio_segment.export(tmp_file_name, format="wav")
        logging.info('wav file exported to {}'.format(tmp_file_name))
        conversion_time = time.time() - conversion_start_time
        decode_time_start_time = time.time()
        text = decode_wav_stream(tmp_file_name, decoder)
        decode_time = time.time() - decode_time_start_time
    else:
        decode_time_start_time = time.time()
        text = decode_wav_stream(audio_file, decoder)
        decode_time = time.time() - decode_time_start_time
        conversion_time = 0
    decode_result[audio_file] = (duration, decode_time, conversion_time, text)
    return decode_result


def decode_wav_stream(wav_file, my_decoder):
    wav_stream = open(wav_file, 'rb')
    my_decoder.start_utt()
    while True:
        buf = wav_stream.read(1024)
        if buf:
            my_decoder.process_raw(buf, False, False)
        else:
            break
    my_decoder.end_utt()
    wav_stream.close()
    hypothesis = my_decoder.hyp()
    try:
        text = hypothesis.hypstr
    except AttributeError:
        text = ''
    return text


def print_results(results, indir):
    total_duration = 0
    total_decode_time = 0
    total_conversion_time = 0
    outfile = os.path.normpath(indir) + '_py.hyp'
    with open(outfile, mode='w') as result_writer:
        logging.info('writing results to {}'.format(outfile))
        for filename, v in results.items():
            # print('{} {}'.format(filename, v))
            logging.info('{} {}'.format(filename, v))
            file_duration, file_decode_time, file_conversion_time, transcription = v
            total_duration += file_duration
            total_decode_time += file_decode_time
            total_conversion_time += file_conversion_time
            fileid, ext = os.path.splitext(os.path.basename(filename))
            fileid = ' ('+fileid+')\n'
            result_writer.write(transcription + fileid)
    print('total audio duration: {:.2f} minutes'.format(total_duration/60))
    print('total decode time: {:.2f} minutes'.format(total_decode_time/60))
    print('total conversion time: {:.2f} minutes'.format(total_conversion_time/60))