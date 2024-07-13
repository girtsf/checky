#!/usr/bin/env python3

import dataclasses
import pathlib
import sys

import sanic
import sanic.response
import tomllib

STATIC_DIR = pathlib.Path(__file__).parent / "static"

app = sanic.Sanic("Checky")
app.static("/", STATIC_DIR, index="index.html")


@dataclasses.dataclass
class CsvFileConfig:
    # Fields to search.
    search: list[str]
    # Field to use for linking records together.
    key: str
    # Fields to show.
    show: list[str]


@dataclasses.dataclass
class Config:
    files: dict[str, CsvFileConfig]

    @classmethod
    def from_file(cls, config_file: pathlib.Path) -> "Config":
        text = config_file.read_text()
        parsed = tomllib.loads(text)
        return cls(files={k: CsvFileConfig(**v) for k, v in parsed.items()})



@app.before_server_start
async def parse_args(app, loop):
    if len(sys.argv) != 2:
        print("Usage: checky.py <dir>")
        sys.exit(1)

    app.ctx.csv_dir = pathlib.Path(sys.argv[1])
    if not app.ctx.csv_dir.is_dir():
        print(f"{app.ctx.csv_dir} is not a directory")
        sys.exit(1)
    print(f"Using {app.ctx.csv_dir} as CSV directory")
    print(Config.from_file(app.ctx.csv_dir / "config.toml"))


@app.post("/search")
async def search(request):
    print(request)
    return sanic.response.text(f"foo {app.ctx.csv_dir}")


def main():
    app.run(dev=True, host="0.0.0.0")


if __name__ == "__main__":
    main()
