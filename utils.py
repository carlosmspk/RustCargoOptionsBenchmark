from itertools import product
import json
from os.path import exists
import subprocess
from time import perf_counter
from datetime import datetime

OUT_REL_PATH = "target/release/rust_cargo_options_benchmark"
FIRST_BUILD = True
COMMON_CARGO_HEADER = '[package]\nname = "rust_cargo_options_benchmark"\nversion = "0.1.0"\nedition = "2021"\n\n[features]\ndefault = [\n  "tokio/full",\n]\n\n[dependencies]\nstatic-rc = "0.6.0"\nanyhow = "1.0.65"\nserde = {version = "1.0.144", features = ["derive"]}\nserde_json = {version = "1.0.85", features = ["float_roundtrip", "preserve_order"]}\nlasso = "0.6.0"\nlazy_static = "1.4.0"\nmd5 = "0.7.0"\ntokio = "1.20.0"\n\n'

def read_param_json() -> dict:
    with open("params_to_try.json", "r") as f:
        result = json.loads(f.read())
    return result

def write_option_to_cargo_toml(options: dict):
    if not exists("Cargo.toml"):
        print("Cargo.toml does not exist in this directory")
        exit(1)
    config = COMMON_CARGO_HEADER + "[profile.release]\n"

    for field, value in options.items():
        config += field + " = " + value + "\n"

    with open("Cargo.toml", "w") as f:
        f.write(config)


def create_option_permutations(options_dict: dict) -> list[dict]:
    keys, values = zip(*options_dict.items())
    option_permutations = [dict(zip(keys, v)) for v in product(*values)]
    return option_permutations


def run(command: str) -> subprocess.CompletedProcess[str]:
    command_args = command.split(" ")

    process_status = subprocess.run(
        command_args, capture_output=True, text=True, universal_newlines=True
    )

    check_output_and_log(process_status)

    return process_status


def check_output_and_log(process_out: subprocess.CompletedProcess[str]):
    commands = " ".join([*process_out.args])

    if process_out.returncode != 0:
        print(f"<{commands.upper()} ERROR>: stderr written to err.log")
        with open("error.log", "a") as f:
            f.write(
                datetime.now().strftime(
                    "=================================================================================================\n%m/%d/%Y, %H:%M:%S\n"
                )
            )
            f.write(f"Command: {commands}\nStderr below:\n\n")
            f.write(process_out.stderr)
            f.write("\n")


def convert_string_to_bytes(memory_size_string: str) -> int:
    CONVERSION_DICT = {
        "B": 1,
        "K": 1024,
        "M": 1024**2,
        "G": 1024**3,
    }
    unit_scale = 0
    number = ""
    for char in memory_size_string:
        if char.isnumeric() or char == ".":
            number += char
        else:
            unit_scale = CONVERSION_DICT[char]
    adimensional_value = float(number)
    true_value = adimensional_value * unit_scale
    true_value = int(true_value)
    return true_value


def build() -> float:
    run("cargo clean")

    start = perf_counter()
    run("cargo build --release")
    build_time = perf_counter() - start
    return build_time


def compute_bin_size() -> int:
    output = run(f"du -h {OUT_REL_PATH}")
    size = output.stdout.split("\t")[0]
    size = convert_string_to_bytes(size)
    return size


def runtime() -> float:
    start = perf_counter()
    run("cargo run --release")
    run_time = perf_counter() - start
    return run_time


def benchmark_instance(option_set: dict, print_commands=True) -> dict:
    global FIRST_BUILD
    write_option_to_cargo_toml(option_set)
    if FIRST_BUILD:
        build()
        runtime()
        compute_bin_size()
        FIRST_BUILD = False
    PRINT_COMMANDS = print_commands
    return {
        "build_time": build(),
        "run_time": runtime(),
        "bin_size": compute_bin_size(),
    }
