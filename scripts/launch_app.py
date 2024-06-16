import argparse
from pathlib import Path

from resq.logger.logger import init_logger
from resq.app.app import app

def app_manager(
):

    # Retrieve arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port",
        dest="port",
        default=7860,
        help="Server port",
    )
    parser.add_argument(
        "-i", "--ip",
        dest="ip",
        default="0.0.0.0",
        help="Server IP",
    )
    parser.add_argument(
        "-l", "--log",
        dest="logs_path",
        default="./logs/",
        help="Paths to logs",
    )
    parser.add_argument(
        "-s", "--share",
        action="store_true"
    )
    args = parser.parse_args()

    # Initialize logger
    init_logger(
        console_output=True,
        logfile=True,
        logfolder_path=Path(args.logs_path),
        logfile_name="app_log",
    )


    app(
        args.ip,
        args.port,
        args.share,
        Path(args.logs_path)
    )
    
if __name__ == "__main__":
    app_manager()