### Hardware & Memory Modeling
* [cite_start]**Device Profiles:** Models an 8-device decode node matching the peak compute throughput (2,250 TFLOPS) and read bandwidth (8 TB/s) of an NVIDIA B200 GPU[cite: 156].
* [cite_start]**Memory Configurations:** Simulates devices equipped with either 256 GB of HBM4 or five 512 GB HBF stacks[cite: 157]. [cite_start]For HBM setups, it models direct access to CPU memory via NVLink-C2C without explicit memory copies[cite: 159].
* [cite_start]**Interconnect:** Simulates an NVL72-like topology using NVLink5.0, providing 900 GB/s of unidirectional bandwidth[cite: 158].
* [cite_start]**HBF Parameters:** Configures HBF read latency ($t_R$) at $3~\mu s$ [cite: 102][cite_start], write latency ($t_{PROG}$) at $100~\mu s$ [cite: 102][cite_start], and per-stack write bandwidth at 48 GB/s[cite: 104].

### System & Caching Architecture
* [cite_start]**On-Chip SRAM Buffering:** Implements double buffering to hide HBF read latency [cite: 165][cite_start], KV cache write buffering [cite: 167] [cite_start](stream-written to HBF once per decode stage [cite: 168]), and input/output activation buffering[cite: 169]. [cite_start]Assumes an aggregate on-chip bandwidth of 16.8 TB/s per device[cite: 169].
* [cite_start]**Data Placement:** Simulates request-local KV cache placement, where each request's KV cache is allocated in a contiguous logical HBF region and appended in token order[cite: 191].
* [cite_start]**I/O Streams & Wear:** Models continuous batching as multiple request-local sequential read streams and buffered KV cache updates as append-only sequential write streams[cite: 192]. [cite_start]Applies a Write Amplification Factor (WAF) of 1.02 to model flash wear[cite: 194].

### Model & Workload Execution
* [cite_start]**Weight Distribution:** Models device-level core attention scheduling[cite: 162]. [cite_start]Non-MoE and shared expert weights are duplicated across all devices, while gated expert weights are uniquely distributed to a single device[cite: 162].
* [cite_start]**Workload Skew:** Utilizes synthesized datasets with a highly skewed Zipfian distribution (skewness factor of 0.8) to model token-to-expert assignments[cite: 163].
* [cite_start]**Attention Mechanisms:** Supports Grouped-Query Attention (GQA) and Multi-head Latent Attention (MLA) modeling using BF16 precision[cite: 160].