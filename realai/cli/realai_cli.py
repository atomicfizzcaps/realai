"""Command-line entrypoint for structured RealAI workflows."""

import argparse

from realai import main as demo_main
from realai.server.app import main as serve_main


def build_parser():
    """Build the RealAI CLI argument parser."""
    parser = argparse.ArgumentParser(description='RealAI command-line interface.')
    subcommands = parser.add_subparsers(dest='command')

    serve_parser = subcommands.add_parser('serve', help='Run the structured inference server.')
    serve_parser.add_argument('--host', default='0.0.0.0')
    serve_parser.add_argument('--port', default=8000, type=int)

    subcommands.add_parser('demo', help='Run the existing RealAI demo flow.')
    return parser


def main(argv=None):
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == 'serve':
        serve_main(host=args.host, port=args.port)
        return 0
    demo_main()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
