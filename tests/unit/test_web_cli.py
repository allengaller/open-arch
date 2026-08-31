from openarch.main import parse_args


def test_parse_args_default_is_console():
    args = parse_args([])
    assert args.command is None


def test_parse_args_web_with_overrides():
    args = parse_args(["web", "--host", "0.0.0.0", "--port", "9000"])
    assert args.command == "web"
    assert args.host == "0.0.0.0"
    assert args.port == 9000


def test_parse_args_web_defaults():
    args = parse_args(["web"])
    assert args.command == "web"
    assert args.host is None
    assert args.port is None
