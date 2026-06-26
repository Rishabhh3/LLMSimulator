# LLMSimulator Architecture

## Overview

LLMSimulator is a **cycle-accurate LLM inference simulator** written in C++ that models the execution of large language models on distributed GPU systems with optional PIM (Processing-in-Memory) and Logic processors. It integrates Ramulator 2.0 for detailed DRAM timing simulation.

---

## Directory Structure

```
LLMSimulator/
├── CMakeLists.txt                  # Top-level build: defines llm_system shared library
├── config.yaml                     # Main simulation configuration
├── dram_config.yaml                # DRAM config (HBM3 default)
├── dram_config_HBM3_80GB.yaml      # HBM3 80GB DRAM config
├── dram_config_HBM3E_192GB.yaml    # HBM3E 192GB DRAM config
├── memory_pool_dram_config.yaml    # LPDDR5 memory pool config
├── .gitmodules                     # Ramulator 2.0 submodule
│
├── eval/                           # Entry point
│   ├── CMakeLists.txt              # Builds `run` executable
│   └── test.cpp                    # main(): reads config, builds Model, runs simulation
│
├── src/
│   ├── CMakeLists.txt              # Aggregates 5 subdirectories
│   │
│   ├── common/                     # Shared type aliases & utilities
│   │   ├── type.h                  # hw_metric, cycle_t, time_ns, addr, energy_nJ
│   │   └── assert.h                # fail(), assertTrue(), warn(), notYetImplemented()
│   │
│   ├── dram/                       # DRAM & PIM subsystem
│   │   ├── CMakeLists.txt          # Static lib `dram` + pimkernel + ramulator2
│   │   ├── dram_type.h             # Enums: DRAMRequestType, PIMCommandType, PIMOperandType
│   │   ├── dram_interface.h/cpp    # Bridges LLMSimulator <-> Ramulator 2.0
│   │   ├── dram_request.h/cpp      # DRAM request abstraction
│   │   ├── pim_request.h/cpp       # PIM-specific request
│   │   ├── memory_config.h         # MemoryConfig: HBM3/HBM3E cube/channel/rank layout
│   │   ├── memory_object.h/cpp     # Abstract memory block
│   │   ├── mmap_controller.h/cpp   # Memory-mapped address translation
│   │   ├── data_object.h/cpp       # Data payload for transactions
│   │   ├── power.h                 # Power estimation (DramEnergy structs)
│   │   ├── test.cpp                # Unit tests
│   │   │
│   │   ├── pimkernel/              # PIM kernel library
│   │   │   ├── pim_kernel.h/cpp    # Kernel registry: Read, Write, Mult, Add, MAD, GEMV...
│   │   │   ├── GEMV.cpp            # Matrix-vector PIM kernel
│   │   │   ├── Read.cpp            # PIM Read kernel
│   │   │   └── Write.cpp           # PIM Write kernel
│   │   │
│   │   └── ramulator2/             # Git submodule: modified Ramulator 2.0
│   │       ├── CMakeLists.txt
│   │       ├── ext/                # Dependencies: argparse, spdlog, yaml-cpp
│   │       └── src/
│   │           ├── main.cpp        # Standalone Ramulator executable
│   │           ├── base/           # Config, Factory, Logging, Stats, Request, Clocked
│   │           ├── addr_mapper/    # RoBaRaCoCh, Linear, RIT
│   │           ├── dram/           # DDR3/4/5, HBM/HBM2/HBM3, GDDR6, LPDDR5
│   │           ├── dram_controller/# Generic, PIM, BH controllers + schedulers
│   │           ├── frontend/       # gem5, trace, PIM, O3 frontends
│   │           ├── memory_system/  # Generic/PIM/BH/DRAM wrappers
│   │           └── translation/    # Address translation (none, random)
│   │
│   ├── hardware/                   # Hardware system modeling
│   │   ├── CMakeLists.txt          # Object lib `hardware`
│   │   ├── base.h                  # ProcessorType enum, LayerType enum, LayerInfo, ptr aliases
│   │   ├── hardware_config.h       # SystemConfig: GPU presets (A100/H100/B100/B200)
│   │   ├── stat.h                  # Stat: per-iteration simulation results
│   │   ├── cluster.h/cpp           # Cluster: multi-node orchestrator, runs iterations
│   │   ├── node.h/cpp              # Node: a single server w/ multiple devices
│   │   ├── device.h/cpp            # Device: one GPU/accelerator w/ compute & memory
│   │   ├── executor.h/cpp          # Executor: dispatches LayerType to hardware impls
│   │   ├── layer_impl.h/cpp        # Base layer implementation utilities
│   │   ├── activation_impl.cpp     # Activation function hardware timing
│   │   ├── linear_impl.cpp         # Linear layer hardware timing
│   │   ├── attention_gen_impl.cpp  # Attention Q*K generation hardware timing
│   │   ├── attention_sum_impl.cpp  # Attention softmax*V hardware timing
│   │   ├── attention_mixed_impl.cpp# Mixed attention hardware timing
│   │   └── test.cpp                # Unit tests
│   │
│   ├── model/                      # LLM model definitions
│   │   ├── CMakeLists.txt          # Object lib `model`
│   │   ├── model_config.h          # ModelConfig: Mixtral, DeepSeekV3, Llama3/4, Grok1 presets
│   │   ├── model.h                 # Model: top-level Module, distributes across devices
│   │   ├── llm.h/cpp               # LLM: constructs full transformer computation graph
│   │   ├── util.h                  # set_device_list() helper
│   │   └── test.cpp                # Unit tests
│   │
│   ├── module/                     # Computation graph nodes (Module library)
│   │   ├── CMakeLists.txt          # Object lib `module`
│   │   ├── base.h                  # Tensor_Ptr, TensorVec, kvCacheKey
│   │   ├── module.h/cpp            # Module base class: sub-modules, tensors, forward()
│   │   ├── module_graph.h/cpp      # ModuleGraph DAG, TopModuleGraph: execution orchestration
│   │   ├── tensor.h/cpp            # Tensor: shape, memory region, device affinity
│   │   ├── status.h                # ExecStatus, StatusBoard: timing/energy tracking
│   │   ├── timeboard.h/cpp         # TimeBoard: timeline & Gantt chart export
│   │   ├── activation.h/cpp        # Activation (ReLU, SwiGLU)
│   │   ├── attention.h/cpp         # Attention (MHA, GQA, MQA, MLA, Absorbed MLA)
│   │   ├── communication.h/cpp     # Inter-device data transfer (NVLink, InfiniBand)
│   │   ├── compressed_kv_restore.h/cpp  # Compressed KV cache restore
│   │   ├── decoder.h/cpp           # Transformer decoder (dense + MoE variants)
│   │   ├── embedding.h/cpp         # Token embedding
│   │   ├── expert.h/cpp            # MoE expert FFN
│   │   ├── layer.h/cpp             # Generic transformer layer (attention + FFN)
│   │   ├── layernorm.h/cpp         # LayerNorm, RMSNorm
│   │   ├── linear.h/cpp            # Linear (dense + batched)
│   │   ├── lm_head.h/cpp           # Language model head
│   │   ├── parallel.h/cpp          # Parallel split/merge across processors
│   │   ├── residual.h/cpp          # Residual connections
│   │   ├── rope.h/cpp              # Rotary Position Embedding
│   │   ├── route.h/cpp             # MoE routing
│   │   └── test.cpp                # Unit tests
│   │
│   └── scheduler/                  # Request scheduling & batching
│       ├── CMakeLists.txt          # Object lib `scheduler`
│       ├── scheduler.h/cpp         # Scheduler: queue management, batching, sequence scheduling
│       ├── sequence.h/cpp          # Sequence: per-request state, BatchedSequence: batch grouping
│       └── test.cpp                # Unit tests
│
├── patch/
│   └── ramulator2_pim.patch        # Git patch adding PIM support to Ramulator 2.0
│
└── build/                          # Compiled output
```

---

## Component Responsibilities

### 1. Entry Point (`eval/test.cpp`)

- Reads `config.yaml` (or CLI-provided path)
- Configures `SystemConfig` (GPU gen, NVLink gen, InfiniBand gen)
- Selects `ModelConfig` from model name (deepseekV3, llama, mixtral, grok1, etc.)
- Creates `Scheduler` (request/sequence management), `Cluster` (hardware), `Model` (network graph)
- Runs iterations via `cluster->runIteration(iter)`
- Exports Gantt charts and CSV statistics

### 2. Configuration (`config.yaml`, `hardware_config.h`, `model_config.h`)

| File | Purpose |
|------|---------|
| `config.yaml` | Simulation parameters: model, system topology, optimization flags, serving params, logging |
| `hardware_config.h` | `SystemConfig` class w/ GPU presets (A100/H100/B100/B200) — FLOPS, bandwidth, memory |
| `model_config.h` | `ModelConfig` class w/ LLM presets (Mixtral, DeepSeekV3, Llama 3/4, Grok, OpenMoE) |

### 3. Scheduler (`src/scheduler/`)

- **`Scheduler`**: Manages the sequence queue, creates batches, handles prefill/decode modes
  - Supports synthetic and real data, Zipfian expert distribution
  - Continuous batching: tracks sequences across the prefill-then-decode lifecycle
  - `running_queue`: currently active `BatchedSequence` objects
  - `setMetadata()`/`getMetadata()`: batch partition across data-parallel ranks
- **`Sequence`**: Represents one request (input/output length, expert allocation, timing)
- **`BatchedSequence`**: Groups sequences for batched execution; tracks per-expert token counts

### 4. Hardware System (`src/hardware/`)

- **`Cluster`**: Top-level orchestrator — owns `Node`s, manages iteration lifecycle
  - `runIteration()`: main simulation loop (prefill + decode steps)
  - `execution_time_cache`: memoizes `ExecStatus` per `(LayerType, ProcessorType, DRAMRequestType, size)`
- **`Node`**: Represents a server — owns `Device`s, inter-node communication via `node_ict_*`
- **`Device`**: A single GPU/accelerator — owns a `TopModuleGraph`, `DRAMInterface`, `StatusBoard`
  - `execution()`: called by the `ModuleGraph` to run a layer on this device
  - Routes to Ramulator (`use_ramulator=true`) or ideal timing model
- **`Executor`**: Layer-type dispatcher — maps `LayerType` + `ProcessorType` to hardware-timed implementations
  - Maintains function pointer tables for: Linear, BatchedLinear, Activation, AttentionGen/Sum/Mixed, MLAGen/Sum/Mixed, AbsorbedMLAGen/Sum
  - Calls into `linear_impl.cpp`, `activation_impl.cpp`, `attention_*_impl.cpp`
- **`SystemConfig`**: Hardware parameters — FLOPS, bandwidths, latencies, processor types

### 5. LLM Model (`src/model/`)

- **`Model`**: Distributes LLM across devices, creates `LLM` on each device
- **`LLM`** (`llm.cpp`): Constructs the complete transformer graph:
  - Embedding → Decoder layers (`num_layers` ×) → LM Head
  - Each decoder = Attention (SelfAttention or MultiLatentAttention) + FFN (dense or MoE)
  - Supports: MHA, GQA, MQA, MLA, Absorbed MLA, Flash Attention
  - MoE: Router → Top-K experts, shared experts

### 6. Module Library (`src/module/`)

- **`Module`**: Base class — recursive tree of sub-modules, tensor management, forward pass
  - `operator()` connects the module graph via tensor passing
  - `graph_execution=true` means the module is a leaf node that dispatches to hardware
- **`ModuleGraph`**: DAG wrapper around a `Module` — manages input/output tensors, readiness, dependencies
- **`TopModuleGraph`**: Device-level execution scheduler — runs `ModuleGraph`s in sequence, manages `TimeBoard`
- **Module types** (all leaf nodes mapped to hardware):
  - `Linear` / `BatchedLinear`: matrix multiplications
  - `Activation`: SwiGLU, ReLU, etc.
  - `SelfAttentionGen`/`Sum`/`Mixed`: standard attention split
  - `MultiLatentAttentionGen`/`Sum`/`Mixed`: DeepSeek-style MLA
  - `AbsorbMLAGen`/`Sum`: Absorbed MLA variant
  - `AttentionSplit`/`Merge`: Split/merge for distributed attention
  - `Decoder` / `MoEDecoder`: Transformer decoder layer (container)
  - `Embedding`, `LMHead`, `LayerNorm`, `RoPE`, `Residual`, `Route`, `Expert`
  - `Parallel`: executes sub-modules on high/low processors concurrently
  - `Communication`: models inter-device data transfer
  - `CompressedKVRestore`: decompresses KV cache for MLA
- **`Tensor`**: Multi-dimensional data buffer — shape, type, memory region (weight/act/cache), device, memory mapping
- **`TimeBoard`**: Records start/end times of each module execution; exports Gantt charts
- **`ExecStatus`**: Per-execution metrics (duration, FLOPS, command counts)
- **`StatusBoard`**: Accumulated device-level metrics (energy, utilization, time)

### 7. DRAM Subsystem (`src/dram/`)

- **`DRAMInterface`**: Bridge to Ramulator 2.0
  - `HandleRequest()`: sends DRAM/PIM requests to Ramulator
  - `GeneratePIMCommand()`: translates `DRAMRequest` → `PIMRequest` with command+operands
  - Tracks `ExecStatus` (command counts, timing)
- **`DRAMRequest`**: Generic memory request (address, type, PIM operands)
- **`PIMRequest`**: PIM-specific request for in-memory compute
- **`dram_type.h`**: Enums for all operation types:
  - `DRAMRequestType`: Read, Write, Mult, Add, MAD, GEMV, Tensor, etc.
  - `PIMCommandType`: Add, Sub, Mult, MAC, DRAM2RF, RF2DRAM
  - `PIMOperandType`: RF, DRAM, Src, Precomputed, Dest
- **PIM Kernels** (`pimkernel/`): `Read`, `Write`, `GEMV` implementations
- **Ramulator 2.0**: Cycle-level DRAM simulator — models DRAM standards, controllers, schedulers, address mapping; patched for PIM support

### 8. Common (`src/common/`)

- **`type.h`**: Fundamental type aliases throughout the codebase
- **`assert.h`**: Runtime checking utilities

---

## Data Flow

```
config.yaml
    │
    ▼
eval/test.cpp  ──►  SystemConfig  ──►  Scheduler  ──►  Sequence Queue
    │                                     │
    │                                     ▼
    │                              BatchedSequence
    │                                     │
    │                                     ▼
    │                              Cluster::runIteration()
    │                                     │
    │                                     ▼
    │                              Node::run() → Device::run()
    │                                     │
    │                                     ▼
    │                              TopModuleGraph::run()
    │                                     │
    │                                     ▼
    │                              ModuleGraph::run()
    │                                     │
    │                          ┌──────────┴──────────┐
    │                          ▼                     ▼
    │                   Module::forward()     Module::forward()
    │                   (container nodes)     (leaf/graph nodes)
    │                          │                     │
    │                          ▼                     ▼
    │                   Device::execution()   Executor::execution()
    │                          │                     │
    │                          ▼                     ▼
    │                   ┌──────┴──────┐     linear_impl.cpp
    │                   ▼             ▼     activation_impl.cpp
    │            use_ramulator    ideal     attention_*_impl.cpp
    │                   │
    │                   ▼
    │            DRAMInterface::HandleRequest()
    │                   │
    │                   ▼
    │            Ramulator 2.0 (DRAM timing)
    │
    ▼
  CSV stats + Gantt charts
```

---

## Execution Phases

1. **Prefill**: Processes input tokens in parallel. Batched sequences compute attention over the full input.
2. **Decode**: Generates tokens one at a time with KV cache reuse. Each step processes one new token per sequence.
3. The simulator alternates between these phases based on `prefill_mode` / `decode_mode` config flags.

---

## Key Design Patterns

- **`enable_shared_from_this`**: All major objects (Cluster, Node, Device, Module, Tensor, Sequence) use `shared_ptr` ownership with `Create()` factory methods
- **Module Graph**: Computation is expressed as a DAG of `Module` objects. The `ModuleGraph` wrapper handles dependency tracking and readiness. `TopModuleGraph` sequences execution on each device.
- **Executor Dispatch**: `Executor` maps `(LayerType, ProcessorType)` → function pointer via lookup tables initialized in `initLinear()`, `initActivation()`, etc.
- **DRAM Abstraction**: `Device::execution()` routes to either Ramulator (cycle-accurate) or ideal timing model. The `execution_time_cache` memoizes results for repeated operations.
- **Model Distribution**: `Model` constructor creates `LLM` on each device; `model_distribute()` populates the graph via `top_module->operator()(input_tensor, metadata)`.

---

## Supported LLM Architectures

| Model | Attention | FFN Type | Config Source |
|-------|-----------|----------|---------------|
| Mixtral 8x7B | GQA (KV=8) | MoE (8 experts, top-2) | `model_config.h` |
| OpenMoE | MHA | MoE (32 experts, top-2) | `model_config.h` |
| Grok-1 | GQA (KV=8) | MoE (8 experts, top-2) | `model_config.h` |
| DeepSeek-V3 | MLA (q_lora_rank=1536, kv_lora_rank=512) | MoE (256 experts, top-8) | `model_config.h` |
| Llama 3 405B | GQA (KV=8) | Dense | `model_config.h` |
| Llama 4 Scout | GQA (KV=8) | MoE (16 experts, top-1) | `model_config.h` |
| Llama 4 Maverick | GQA (KV=8) | MoE (128 experts, top-1) | `model_config.h` |

---

## Supported GPU Presets

| GPU | FLOPS (FP16) | Memory BW | Memory Capacity | NVLink |
|-----|-------------|-----------|-----------------|--------|
| A100 | 312 TFLOPS | 2.039 TB/s | 80 GB | Gen 3 (150 GB/s) |
| H100 | 989.4 TFLOPS | 3.352 TB/s | 80 GB | Gen 4 (450 GB/s) |
| B100 | 1750 TFLOPS | 8.0 TB/s | 192 GB | Gen 5 (900 GB/s) |
| B200 | 2250 TFLOPS | 8.0 TB/s | 192 GB | Gen 5 (900 GB/s) |
