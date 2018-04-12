#!/usr/bin/python
import log_generator
import os
from multiprocessing import Process

# default argument values
_log_lines = 5
_file_prefix = ''
_output_type = 'CONSOLE'
_log_type = ['apache']
_sleep_time = 0.0
_file_size_limit = None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(__file__, description="Fake Apache Log Generator")
    parser.add_argument("--output", "-o", dest='output_type', help="Write to a Log file, a gzip file or to STDOUT",
                        choices=['LOG', 'GZ', 'CONSOLE'], default=_output_type)
    parser.add_argument("--num", "-n", dest='num_lines', help=("Number of statements to generate (0 for infinite)."
                        "Note this does not include startup and shutdown statements"),
                        type=int, default=_log_lines)
    parser.add_argument("--prefix", "-p", dest='file_prefix', help="Prefix the output file name", type=str,
                        default=_file_prefix)
    parser.add_argument("--sleep", "-s", dest='sleep_time', help="Sleep this long between lines (in seconds)",
                        default=_sleep_time, type=float)
    parser.add_argument("--type", "-t", nargs="+", dest='log_type',
                        help="Specify the types of log you wish to generate",
                        choices=log_generator.common.log_types, default=_log_type, type=str)
    parser.add_argument("--file-size-limit", "-l", dest='file_size_limit', help="specify the maximum file size in mb",
                        type=int, default=_file_size_limit)
    parser.add_argument("--output-dir", "-d", dest='output_dir', help="The directory to output logs to", type=str,
                        default=os.path.join(".", "logs"))
    parser.add_argument("--max-dither", "-f", dest='dither', type=float, default=0.0,
                        help="causes the interval to dither randomly between 0 and the provided  value")
    args = parser.parse_args()
    processes = []

    for t in args.log_type:
        processes.append(Process(target=getattr(log_generator, t).Generator().generate,
                                 kwargs={
                                     'output_type': args.output_type,
                                     'log_lines': args.num_lines,
                                     'file_prefix': os.path.join(args.output_dir, args.file_prefix),
                                     'sleep_time': args.sleep_time,
                                     'limit': args.file_size_limit,
                                     'max_dither': args.dither
                                     }))
    for p in processes:
        p.start()

    for p in processes:
        p.join()
