import logging
import logging.config
import logging.config
import logging.handlers
import pathlib
from multiprocessing import Pool, Queue, Event, Process, cpu_count
from pathlib import Path

import click

logger = logging.getLogger(__name__)

from insurancedb.file_processor import process_paths
from insurancedb.exporters.file_exporter import to_csv
from insurancedb.log.config import get_log_config, worker_log_initializer, get_dispatch_log_config
from insurancedb.log.listener import listener_process
from insurancedb.utils import chunk_even_groups


def create_db_serial(pdfs_dir: Path, out_dir: Path, root_logger_level: str, app_logger_level: str, log_to_file: bool):
    if out_dir is None:
        out_dir = pdfs_dir

    logging.config.dictConfig(get_log_config(root_logger_level=root_logger_level, app_logger_level=app_logger_level,
                                             log_dir=out_dir, to_file=log_to_file))
    logger.info('Creating db in serial mode.')

    paths = list(pdfs_dir.rglob("*.pdf"))
    data = process_paths(paths)

    to_csv(data, out_dir)


def create_db_parallel(pdfs_dir: Path, out_dir: Path, root_logger_level: str, app_logger_level: str,
                       log_to_file: bool):
    if out_dir is None:
        out_dir = pdfs_dir

    q = Queue()
    worker_log_config = get_dispatch_log_config(q, root_logger_level=root_logger_level,
                                                app_logger_level=app_logger_level)
    worker_log_initializer(worker_log_config)

    listener_log_config = get_log_config(root_logger_level=root_logger_level, app_logger_level=app_logger_level,
                                         log_dir=out_dir, to_file=log_to_file)
    stop_event = Event()
    lp = Process(target=listener_process, name='listener',
                 args=(q, stop_event, listener_log_config))
    lp.start()

    # ----------------------------------------------------
    logger.info('Creating db in multiprocessing mode.')

    paths = list(pdfs_dir.rglob("*.pdf"))
    paths_chunked = list(chunk_even_groups(paths, cpu_count()))

    with Pool(cpu_count(), initializer=worker_log_initializer, initargs=(worker_log_config,)) as pool:
        data_parallel = pool.map(process_paths, paths_chunked)
        data = [item for sublist in data_parallel for item in sublist]

    to_csv(data, out_dir)
    logger.info('Done')
    # ----------------------------------------------------

    stop_event.set()
    lp.join()


@click.command()
@click.argument('pdfs_dir', type=click.Path(path_type=pathlib.Path, exists=True), required=True)
@click.option('--out_dir', type=click.Path(path_type=pathlib.Path, exists=True), required=False)
@click.option('--parallel', type=bool, default=True, show_default=True)
@click.option('--root_logger_level', default='WARN', show_default=True)
@click.option('--app_logger_level', default='INFO', show_default=True)
@click.option('--log_to_file', default=False, show_default=True)
def create_db(pdfs_dir: Path, out_dir: Path, parallel: bool, root_logger_level: str, app_logger_level: str,
              log_to_file: bool):
    if parallel:
        create_db_parallel(pdfs_dir, out_dir, root_logger_level, app_logger_level, log_to_file)
    else:
        create_db_serial(pdfs_dir, out_dir, root_logger_level, app_logger_level, log_to_file)


if __name__ == '__main__':
    create_db()
