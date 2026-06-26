# AGENTS.md — LLMSimulator

## Build

```sh
cd src/dram/ramulator2 && git apply ../../../patch/ramulator2_pim.patch && cd ../..
mkdir -p build && cd build && cmake .. && make -j
```

- **Patch is mandatory** — Ramulator 2.0 submodule won't have PIM support without it
- Single executable: `build/run`
- External deps (yaml-cpp, spdlog, argparse) auto-fetched by CMake via `FetchContent`
- C++17 project; Ramulator 2.0 submodule uses C++20
- CMake copies `config.yaml`, `dram_config_HBM3_80GB.yaml`, `dram_config_HBM3E_192GB.yaml` to build dir
- Expert data CSVs expected at `../expert_data/experts_{model}_{dataset}.csv` when `simulation.data` is not `synthesis` (`eval/test.cpp:206-213`)

## Run

```sh
cd build
./run > test.log
```

- Config via `config.yaml` — YAML-driven simulation parameters
- Output: CSV stats in `../data/` (configurable via `config.yaml log.output_directory`)

## Precision / FLOPS

`precision_byte: 1` (FP8/INT8 in config.yaml) **doubles** `system_config.compute_peak_flops` relative to the FP16-rated GPU preset (`eval/test.cpp:197-199`). The GPU presets in `hardware_config.h` always store FP16 FLOPS.

## Architecture at a glance

| Directory | Role |
|-----------|------|
| `eval/test.cpp` | Entry point — reads YAML, wires system, runs loop |
| `src/hardware/` | Cluster → Node → Device → Executor — hardware simulation |
| `src/module/` | Computation graph nodes (Linear, Attention, Decoder, etc.) |
| `src/model/` | `LLM` class constructs the full transformer graph |
| `src/scheduler/` | Request queue, continuous batching, sequence management |
| `src/dram/` | DRAMInterface + PIM kernels + Ramulator 2.0 submodule |
| `src/common/` | `type.h` type aliases, `assert.h` utilities |

##  Project Mapping & Context
* **System Map:** Detailed module tracking, file locations, and structural dataflows are documented in `ARCHITECTURE.md`. 
* **Rule:** If you are unsure which files contain a specific structural module or execution block, explicitly read `ARCHITECTURE.md` first before guessing paths or scanning directories.

## Linking quirk

`dram` is a **static library** linked with `-Wl,--whole-archive` in `CMakeLists.txt:19` because it contains the Ramulator 2.0 submodule's objects. Other libraries (`hardware`, `module`, `model`, `scheduler`) are **object libraries**.

## Unusual CMake detail

`src/module/CMakeLists.txt:3` sets `target_compile_definitions(module PRIVATE DEBUG)` — the `DEBUG` preprocessor symbol is defined for all module sources but not elsewhere.

## What's missing (so agents don't look for it)

- **No linting / formatter** — no `.clang-*`, `.editorconfig`, or CI config
- **No test framework** — `test.cpp` files exist in subdirectories but are **not built** (no `add_test`, no `enable_testing()`, no CTest)
- **No root `.gitignore`** — only the ramulator2 submodule has one
- **No CI** — no GitHub Actions, Jenkinsfile, or other CI config

## Style conventions

- C++17, `llm_system` namespace, `#pragma once`
- Factory pattern: `static Create()` returns `shared_ptr`, constructors are private
- `enable_shared_from_this` on all major classes
- Classes use `friend` declarations for closely coupled pairs (e.g., `Device` friends `Executor`/`Cluster`)
- Enums in `dram_type.h` and `hardware/base.h` use explicit integer values
