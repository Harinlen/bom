import sys
import uvicorn


def main():
    uvicorn.run('entry:app', host='127.0.0.1', port=8000)


if __name__ == '__main__':
    sys.exit(main())