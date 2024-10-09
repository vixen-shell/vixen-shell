def handle_args():
    from .parsers import root_parser
    from .handlers import handle_root_args

    handle_root_args(root_parser.parse_args())
