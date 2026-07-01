import re
import csv
import os


def get_step_latency_us(log_path):
    with open(log_path, 'r') as f:
        for line in f:
            match = re.search(r"LLM \|\s*(\d+)us", line)
            if match:
                return int(match.group(1))
    return None


def get_local_batch_size(log_path):
    with open(log_path, 'r') as f:
        for line in f:
            if "LLM |" not in line:
                continue
            match = re.search(r"-> tensor\((\d+),", line)
            if match:
                return int(match.group(1))
    return None


def parse_metadata_from_log(log_path):
    dp_degree = None
    precision = None
    with open(log_path, 'r') as f:
        for line in f:
            m = re.search(r"DP(\d+)", line)
            if m:
                dp_degree = int(m.group(1))
            m = re.search(r"precision_byte(\d+)", line)
            if m:
                precision = int(m.group(1))
            if dp_degree is not None and precision is not None:
                break
    return dp_degree, precision


def get_output_len_from_log(log_path):
    with open(log_path, 'r') as f:
        for line in f:
            m = re.search(r"_(\d+)_(\d+)_GPU_", line)
            if m:
                return int(m.group(2))
    return None


def get_output_len_from_csv(csv_path):
    if not os.path.isfile(csv_path):
        return None
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = row.get('output_len', '0')
            if val and int(val) > 0:
                return int(val)
    return None


def find_csv_path(log_path):
    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.endswith('.csv'):
                return line
    return None


def main():
    log_file = "hbf_run.log"
    config_file = "config.yaml"
    log_path = os.path.join(os.path.dirname(__file__) or '.', log_file)
    config_path = os.path.join(os.path.dirname(__file__) or '.', config_file)

    step_latency_us = get_step_latency_us(log_path)
    local_batch_size = get_local_batch_size(log_path)
    dp_degree, precision = parse_metadata_from_log(log_path)

    if step_latency_us is None:
        print("Error: Could not parse step latency from the log.")
        return
    if local_batch_size is None:
        print("Error: Could not parse local batch size from the log.")
        return

    output_len = get_output_len_from_log(log_path)
    if output_len is None:
        csv_path = find_csv_path(log_path)
        if csv_path:
            output_len = get_output_len_from_csv(csv_path)
    if output_len is None:
        try:
            import yaml
            with open(config_path, 'r') as f:
                cfg = yaml.safe_load(f)
            output_len = cfg.get('simulation', {}).get('output_len', 4096)
        except Exception:
            output_len = 4096

    dp = dp_degree or 1
    global_batch = local_batch_size * dp

    step_latency_ms = step_latency_us / 1000.0
    gen_tokens = output_len - 1
    total_gen_time_us = step_latency_us * gen_tokens
    total_gen_time_ms = total_gen_time_us / 1000.0
    throughput_tok_per_s = global_batch * (1_000_000 / step_latency_us)

    print("=" * 50)
    print("        LLMSimulator DeepSeek-R1 Decode Summary")
    print("=" * 50)
    print(f"Local Batch Size (per device) : {local_batch_size:>6}")
    print(f"Data Parallel Degree          : {dp:>6}")
    print(f"Global Batch Size             : {global_batch:>6}")
    print(f"Precision                     : {precision or '?'} Bytes")
    print(f"Input Length                  : N/A (decode mode)")
    print(f"Output Length (gen tokens)    : {output_len:>6} ({gen_tokens})")
    print(f"Step Latency (TPOT)           : {step_latency_ms:>10.4f} ms")
    print(f"Total Gen Time (full seq)     : {total_gen_time_ms:>10.4f} ms")
    print(f"Throughput                    : {throughput_tok_per_s:>10.1f} tok/s")
    print(f"(1 decode token per step, {gen_tokens} steps per sequence)")
    print("=" * 50)


if __name__ == "__main__":
    main()
