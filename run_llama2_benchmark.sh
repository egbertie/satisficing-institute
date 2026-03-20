#!/bin/bash
# Llama2 Benchmark Script for Azure TEE (Intel TDX)
# This script runs comprehensive benchmarks to measure TEE performance overhead

set -e

echo "=== Llama2 Benchmark for Azure TEE (Intel TDX) ==="

# Configuration
MODEL_NAME="meta-llama/Llama-2-7b-chat-hf"
MODEL_NAME_SHORT="llama-2-7b"
RESULTS_DIR="$HOME/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULT_FILE="$RESULTS_DIR/benchmark_${TIMESTAMP}.txt"

# Ensure results directory exists
mkdir -p $RESULTS_DIR

# Activate virtual environment
source ~/llm_env/bin/activate

# Function to log results
log_result() {
    echo "$1" | tee -a $RESULT_FILE
}

log_result "=== Llama2 TEE Benchmark Results ==="
log_result "Timestamp: $(date)"
log_result "VM Size: Standard_DC8s_v3 (Intel TDX)"
log_result "Model: $MODEL_NAME"
log_result ""

# 1. System Information
echo "Collecting system information..."
log_result "=== System Information ==="
log_result "CPU Info:"
cat /proc/cpuinfo | grep "model name" | head -1 | tee -a $RESULT_FILE
log_result "CPU Cores: $(nproc)"
log_result "Memory: $(free -h | grep Mem | awk '{print $2}')"
log_result "Kernel: $(uname -r)"

# Check TDX status
log_result ""
log_result "=== TEE/TEE Status ==="
if [ -d /sys/firmware/acpi/tables ]; then
    ls -la /sys/firmware/acpi/tables/ | grep -i tdx || true
fi
if [ -d /dev/tdx ]; then
    ls -la /dev/tdx* 2>/dev/null || true
fi
dmesg | grep -i tdx | head -5 || log_result "TDX not found in dmesg"
log_result ""

# 2. Download model if not present
echo "Preparing model..."
cd ~/models

if [ ! -d "$MODEL_NAME_SHORT" ]; then
    log_result "Downloading model (this may take a while)..."
    # Use HuggingFace snapshot download
    python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

model_name = '${MODEL_NAME}'
save_path = '${MODEL_NAME_SHORT}'

print(f'Downloading {model_name}...')
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype='auto')

tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)
print(f'Model saved to {save_path}')
" 2>&1 | tee -a $RESULT_FILE
else
    log_result "Model already exists at ~/models/$MODEL_NAME_SHORT"
fi

# 3. Benchmark 1: Transformer inference with HuggingFace
echo "Running HuggingFace Transformers benchmark..."
log_result ""
log_result "=== Benchmark 1: HuggingFace Transformers ==="

cat > /tmp/benchmark_transformers.py << 'EOF'
import torch
import time
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = sys.argv[1]

print(f"Loading model from {model_path}...")
start = time.time()
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float32)
load_time = time.time() - start
print(f"Model load time: {load_time:.2f}s")

# Warmup
prompt = "The future of artificial intelligence is"
inputs = tokenizer(prompt, return_tensors="pt")
_ = model.generate(**inputs, max_new_tokens=10, do_sample=False)

# Benchmark
test_prompts = [
    "The future of artificial intelligence is",
    "In a world where technology evolves rapidly,",
    "The most important scientific discovery was",
    "Climate change affects our planet by",
    "The benefits of machine learning include"
]

num_runs = 3
total_time = 0
total_tokens = 0

for run in range(num_runs):
    for prompt in test_prompts:
        inputs = tokenizer(prompt, return_tensors="pt")
        start = time.time()
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
        elapsed = time.time() - start
        generated_tokens = outputs.shape[1] - inputs.input_ids.shape[1]
        total_time += elapsed
        total_tokens += generated_tokens

avg_time = total_time / (num_runs * len(test_prompts))
avg_tokens_per_sec = total_tokens / total_time

print(f"\n=== Results ===")
print(f"Average generation time: {avg_time:.2f}s")
print(f"Tokens per second: {avg_tokens_per_sec:.2f}")
print(f"Total tokens generated: {total_tokens}")
print(f"Total time: {total_time:.2f}s")
EOF

python3 /tmp/benchmark_transformers.py ~/models/$MODEL_NAME_SHORT 2>&1 | tee -a $RESULT_FILE

# 4. Benchmark 2: llama.cpp (GGUF format)
echo "Running llama.cpp benchmark..."
log_result ""
log_result "=== Benchmark 2: llama.cpp (CPU Optimized) ==="

# Convert model to GGUF if not exists
GGUF_MODEL="~/models/${MODEL_NAME_SHORT}.gguf"
if [ ! -f "$GGUF_MODEL" ]; then
    log_result "Converting model to GGUF format..."
    cd ~/llama.cpp
    # Use convert-hf-to-gguf.py
    python3 convert_hf_to_gguf.py ~/models/$MODEL_NAME_SHORT --outfile ~/models/${MODEL_NAME_SHORT}-q4_0.gguf --outtype q4_0
fi

# Run llama.cpp benchmark
cd ~/llama.cpp
./main -m ~/models/${MODEL_NAME_SHORT}-q4_0.gguf \
    -p "The future of artificial intelligence is" \
    -n 50 -t $(nproc) --temp 0.7 2>&1 | tee -a $RESULT_FILE

# 5. Benchmark 3: Memory bandwidth test
echo "Running memory bandwidth test..."
log_result ""
log_result "=== Benchmark 3: Memory Bandwidth ==="
python3 -c "
import torch
import time

# Test memory bandwidth with large tensor operations
size = 100000000  # 100M elements (~400MB)
iterations = 10

# CPU test
a = torch.randn(size)
b = torch.randn(size)

# Warmup
_ = a + b

start = time.time()
for _ in range(iterations):
    c = a + b
    _ = c * 0.5
elapsed = time.time() - start

bandwidth_gb_s = (size * 4 * 3 * iterations) / (elapsed * 1e9)  # 4 bytes per float32, 3 operations (read, read, write)
print(f'Memory bandwidth test: {bandwidth_gb_s:.2f} GB/s')
" 2>&1 | tee -a $RESULT_FILE

# 6. Summary
echo "Benchmark complete!"
log_result ""
log_result "=== Benchmark Summary ==="
log_result "Results saved to: $RESULT_FILE"
log_result "Timestamp: $(date)"

# Display summary
cat $RESULT_FILE
