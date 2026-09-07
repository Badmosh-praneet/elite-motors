#!/usr/bin/env python3
"""Start the Volkswagen Elite Motors API + website.

    python run.py
    python run.py --port 9000 --reload
"""
import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Volkswagen Elite Motors API + website")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="Restart on code changes.")
    args = parser.parse_args()

    shown = "localhost" if args.host == "127.0.0.1" else args.host
    base = f"http://{shown}:{args.port}"
    print("=" * 64)
    print("  VOLKSWAGEN ELITE MOTORS")
    print("=" * 64)
    print(f"  Website     {base}")
    print(f"  Swagger UI  {base}/docs")
    print(f"  ReDoc       {base}/redoc")
    print(f"  OpenAPI     {base}/openapi.json")
    print("=" * 64)

    uvicorn.run("api.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
