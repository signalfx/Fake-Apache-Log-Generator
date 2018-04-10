#!/usr/bin/python
import log_generator
from multiprocessing import Process

# default argument values
_log_lines = 5
_file_prefix = None
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
                        choices=['apache', 'apache_error', 'mysql', 'mysql_error'], default=_log_type, type=str)
    parser.add_argument("--file-size-limit", "-l", dest='file_size_limit', help="specify the maximum file size in mb",
                        type=int, default=_file_size_limit)
    args = parser.parse_args()
    processes = []
    for t in args.log_type:
        generator = log_generator.Apache()
        if t == 'mysql_error':
            generator = log_generator.MySQLError()
        elif t == 'apache_error':
            generator = log_generator.ApacheError()
        elif t == 'apache':
            generator = log_generator.Apache()
        elif t == 'mysql':
            generator = log_generator.MySQL()
        processes.append(Process(target=generator.generate,
                                 kwargs={
                                     'output_type': args.output_type,
                                     'log_lines': args.num_lines,
                                     'file_prefix': args.file_prefix,
                                     'sleep_time': args.sleep_time,
                                     'limit': args.file_size_limit
                                     }))
    for p in processes:
        p.start()

    for p in processes:
        p.join()
