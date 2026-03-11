import argparse

from backend.infrastructure.ingest.build_index import build_index_from_file


def main() -> None:
    """Запустить сборку индекса из текстового документа.

    Raises:
        FileNotFoundError: Если входной файл не найден.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    build_index_from_file(args.file)


if __name__ == "__main__":
    main()
