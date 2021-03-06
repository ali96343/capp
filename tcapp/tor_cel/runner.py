import argparse
from server import Server

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Server Runner')
    arg_parser.add_argument('-H',
                            '--host',
                            default='127.0.0.1',
                            help='Server hostname')
    arg_parser.add_argument('-P',
                            '--port',
                            default='8888',
                            help='Server port')
    args = arg_parser.parse_args()

    server = Server(args)
    server.run()
