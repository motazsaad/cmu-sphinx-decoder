import logging
import os
import datetime
logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)


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


def print_results(results, indir):
    total_duration = 0
    total_decode_time = 0
    total_conversion_time = 0
    with open(os.path.normpath(indir) + '.hyp', mode='w') as result_writer:
        logging.info('writing results to {}.hyp'.format(indir))
        for filename, v in results.items():
            # print('debug: {} {}'.format(filename, v))
            file_duration, file_decode_time, file_conversion_time, transcription = v
            total_duration += file_duration
            total_decode_time += file_decode_time
            total_conversion_time += file_conversion_time
            fileid, ext = os.path.splitext(os.path.basename(filename))
            fileid = ' ('+fileid+')\n'
            result_writer.write(transcription + fileid)
    print('total audio duration: {}'.format(datetime.timedelta(seconds=total_duration)))
    print('total decode time: {}'.format(datetime.timedelta(seconds=total_decode_time)))
    print('total conversion time: {}'.format(datetime.timedelta(seconds=total_conversion_time)))