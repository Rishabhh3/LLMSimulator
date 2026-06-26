# LLMSimulator - Agent Guidelines

This repository contains a specialized simulation environment for testing architectural execution blocks, logic gates, and hardware pipelines. Follow these exact patterns to avoid breaking execution trees and wasting token context.

##  Execution & Compilation Commands
Never guess build commands. Use these exact vectors:

* **Build Codebase:** `cmake -B build -S . && cmake --build build`
* **Clean Artifacts:** `rm -rf build/`
* **Run Simulator Binary:** `./build/LLMSimulator` (requires config paths passed as explicit args; look inside `src/main.cpp` or check `--help` for positional arguments).

##  Project Mapping & Context
* **System Map:** Detailed module tracking, file locations, and structural dataflows are documented in `ARCHITECTURE.md`. 
* **Rule:** If you are unsure which files contain a specific structural module or execution block, explicitly read `ARCHITECTURE.md` first before guessing paths or scanning directories.

## Testing & Verification
Verification scripts are locked into specific sub-directories. Do not try to run global `pytest` or basic binary tests.

* **Run Suite:** `ctest --test-dir build --output-on-failure`
* **Target Single Test Component:** `ctest --test-dir build -R <test_name_regex>`

##  Repository Architecture & Boundaries
Understanding boundaries prevents the agent from modifying execution pipelines unexpectedly:

* `src/` - Core simulator mechanics, memory array allocations, and structural modeling blocks.
* `tests/` - Hardware verification assertions. Do not mix test fixtures with core tracking modules.
* `CMakeLists.txt` - The singular source of truth for dependencies and include layouts. Always read this file before assuming a C++ package or external module is available.

## Critical Optimization Rules (KV Cache Safety)
Because this workspace runs with a constrained local memory space (`num_ctx`), you must adhere to strict payload limits:

* **No Echoing/Bloat:** Do not output whole files when writing patches. Modify precisely via target edits.
* **Line Targeting Only:** When reading code paths to trace errors, prioritize reading targeted lines using the line-range tool (`@filename.cpp#L10-30`) rather than reading full multi-thousand-line layout matrices.