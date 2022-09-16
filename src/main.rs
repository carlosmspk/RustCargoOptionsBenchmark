/// source: https://github.com/hanabi1224/Programming-Language-Benchmarks/blob/main/bench/algorithm/binarytrees/4.rs
mod bintree;
/// source: https://github.com/hanabi1224/Programming-Language-Benchmarks/blob/main/bench/algorithm/json-serde/3.rs
mod serde;
mod sieve;

use anyhow;

fn main() -> anyhow::Result<()> {
    bintree::run_benchmark();
    serde::run_benchmark()?;
    sieve::run_benchmark();
    Ok(())
}
