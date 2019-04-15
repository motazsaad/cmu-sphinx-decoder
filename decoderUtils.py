import logging
import os
import sys
import time

import ffmpy
import gc
from pocketsphinx import DefaultConfig, Decoder
from tqdm import tqdm

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)


def load_decoder(myid, model_config, out):
    # Create a decoder with certain model
    pocketsphinx_config = DefaultConfig()
    model_name = model_config.sections()[0]
    hmm = model_config[model_name]['hmm']
    dict = model_config[model_name]['dict']
    lm = model_config[model_name]['lm']
    # logfn = model_config[model_name]['log']
    logfn = '{}_{}.log'.format(out, myid)
    if not os.path.exists(hmm):
        print('ERROR: {} does not exist'.format(hmm))
        sys.exit(-2)
    if not os.path.exists(lm):
        print('ERROR: {} does not exist'.format(lm))
        sys.exit(-4)
    if not os.path.exists(dict):
        print('ERROR: {} does not exist'.format(dict))
        sys.exit(-5)
    pocketsphinx_config.set_string('-hmm', hmm)
    pocketsphinx_config.set_string('-lm', lm)
    pocketsphinx_config.set_string('-dict', dict)
    pocketsphinx_config.set_string('-logfn', logfn)
    decoder_engine = Decoder(pocketsphinx_config)
    return decoder_engine


def split_lists_with_n_elements(data_list, cpus_number):
    """split into lists. Each list has n elements (n = # of cores)"""
    list_size = len(data_list)
    if list_size <= cpus_number:
        return [data_list]
    else:
        return list(chunks(data_list, cpus_number))


def split_n_lists(data, cpus_number):
    """split list into n lists. (n = # of cores)"""
    if len(data) <= cpus_number:
        return [data]
    else:
        part_size = int(len(data) / cpus_number)
        # print('part size {}'.format(part_size))
        parts = [data[x:x + part_size] for x in range(0, len(data), part_size)]
        if len(parts[-1]) < part_size:
            parts[-2].extend(parts[-1])
            del parts[-1]
        return parts


def split_n_lists_uniform(data, number):
    if len(data) <= number:
        return [data]
    m = float(len(data)) / number
    parts = [data[int(m * i):int(m * (i + 1))] for i in range(number)]
    return parts


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for j in range(0, len(l), n):
        yield l[j:j + n]


def decode_audio(audio_file, decoder, log, sample_rate):
    decode_result = {}
    if log:
        logging.info('decode_audio(file:{})'.format(audio_file))
    if not audio_file.endswith('.wav'):
        conversion_start_time = time.time()
        if log:
            logging.info('converting {} to wav'.format(audio_file))
        tmp_file_name = '/tmp/' + os.path.basename(audio_file) + '.wav'
        if os.path.exists(tmp_file_name):
            os.remove(tmp_file_name)
        ff = ffmpy.FFmpeg(inputs={audio_file: None},
                          outputs={tmp_file_name: '-ac 1 -ar {} -loglevel quiet '.format(sample_rate)})
        if log:
            logging.info('conversion cmd: {}'.format(ff.cmd))
            logging.info('wav file converted to {}'.format(tmp_file_name))
        ff.run()
        conversion_time = time.time() - conversion_start_time
        decode_time_start_time = time.time()
        text = decode_wav_stream(tmp_file_name, decoder)
        decode_time = time.time() - decode_time_start_time
        os.remove(tmp_file_name)
        if log:
            logging.info('delete {}'.format(tmp_file_name))
    else:
        decode_time_start_time = time.time()
        text = decode_wav_stream(audio_file, decoder)
        decode_time = time.time() - decode_time_start_time
        conversion_time = 0
    decode_result[audio_file] = text
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


def print_results(myid, results, outfile_prefix, log):
    outfile = "{}_{}.hyp".format(os.path.normpath(outfile_prefix), str(myid))
    with open(outfile, mode='w') as result_writer:
        logging.info('writing results to {}'.format(outfile))
        for filename, transcription in results.items():
            fileid, ext = os.path.splitext(os.path.basename(filename))
            fileid = ' (' + fileid + ')\n'
            result_writer.write(transcription + fileid)


def decode_speech(myid, audio_list, config, in_dir,
                  out, log, sample_rate, progress_outfile):
    logging.info('decoder of process {} with pid {} has been started ...'.format(myid, os.getpid()))
    if log:
        logging.info('input directory: {}'.format(in_dir))
    my_decoder = load_decoder(myid, config, out)
    logging.info('decoder of process {} with pid {} has been loaded ...'.format(myid, os.getpid()))
    ###################################################
    outfile = "{}_{}.hyp".format(os.path.normpath(out), str(myid))
    file_writer = open(outfile, mode='w', buffering=1)
    t1 = time.time()
    # bar = Bar('Progress of process {}, pid {}'.format(myid, os.getpid()), max=len(audio_list))
    if myid != 'seq':
        pbar = tqdm(total=len(audio_list),
                    desc='Progress of process {}, pid {}'.format(myid, os.getpid()),
                    position=int(myid), file=progress_outfile)
    else:
        pbar = tqdm(total=len(audio_list),
                    desc='Progress of process {}, pid {}'.format(myid, os.getpid()),
                    file=progress_outfile)
    for i, audio_file in enumerate(audio_list):
        if log:
            logging.info('decode {}'.format(audio_file))
        result = decode_audio(audio_file, my_decoder, log, sample_rate)
        fileid, ext = os.path.splitext(os.path.basename(audio_file))
        fileid = ' (' + fileid + ')\n'
        file_writer.write(result[audio_file] + fileid)
        # bar.next()
        pbar.update()
        # file_writer.flush() # instead, we used buffering=1 
    # bar.finish()
    pbar.close()

    ##########################################
    t2 = time.time()
    ##########################################
    file_writer.close()
    ##########################################
    print('total time in process {} with pid {}: {:.2f} minutes'.format(myid, os.getgid(), ((t2 - t1) / 60)))
    ##########################################
    gc.collect()
