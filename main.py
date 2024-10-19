import os
import sys
import uvicorn


def main():
    if 'MTC_GAME_SERVER' not in os.environ:
        log_lv = 'debug'
        host_ip = '127.0.0.1'
        host_port = 8000
        worker = 1
    else:
        log_lv = 'error'
        host_ip = '0.0.0.0'
        host_port = 80
        worker = 4
    uvicorn.run('entry:app', host=host_ip, port=host_port,
                log_level=log_lv, workers=worker)


if __name__ == '__main__':
    sys.exit(main())