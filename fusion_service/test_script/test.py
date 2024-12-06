import argparse

parser = argparse.ArgumentParser(description="Process some integers.")

parser.add_argument("--name", type=str, help="Name of the user")

args = parser.parse_args()

print(f"Hello, {args.name}!")
