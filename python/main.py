import sys

from source.game import Game


def main() -> None:
    if len(sys.argv) > 1:
        Game(sys.argv[1]).run()
    else:
        print("Usage - python main.py COM<number>")


if __name__ == '__main__':
    main()
