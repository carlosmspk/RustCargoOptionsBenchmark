from datetime import datetime
import json
import utils
import pandas as pd
from tqdm import tqdm

SAMPLES_PER_OPTION_SET = 10
# OPTION_SETS_TO_TRY = utils.read_param_json()
OPTION_SETS_TO_TRY = {
    "panic": ['"abort"'],
    "strip": ["false"],
    "lto": ["false"],
    "opt-level": ["0"],
    "codegen-units": ["16", "256"],
}

all_options = utils.create_option_permutations(OPTION_SETS_TO_TRY)

results_dict = {
    "panic": [],
    "strip": [],
    "lto": [],
    "opt-level": [],
    "codegen-units": [],
    "build_time": [],
    "run_time": [],
    "bin_size": [],
}
print("\nStarting Benchmark...")
for option_set in tqdm(all_options):
    for i in range(SAMPLES_PER_OPTION_SET):
        for field, value in option_set.items():
            value = value.strip('"')
            results_dict[field].append(value)
        results = utils.benchmark_instance(option_set, print_commands=False)
        for field, value in results.items():
            results_dict[field].append(value)

results_df = pd.DataFrame(results_dict)
timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
results_df.to_csv(f"results/{timestamp}_benchmark_results.csv", index_label="id")
