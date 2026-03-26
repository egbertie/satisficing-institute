#!/bin/bash
# Setup Python environment and LLM inference framework on TEE VM
# Run this script on the Azure DC8s_v3 VM after deployment

set -e

echo "=== Setting up Python Environment for TEE LLM Inference ==="

# 1. System update and dependencies
echo "Updating system packages..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    wget \
    curl \
    htop \
    numactl \
    linux-tools-common \
    linux-tools-generic

# 2. Install Intel SGX/TEE drivers and tools (for TDX support)
echo "Installing Intel TDX tools..."
# Check if TDX is available
cat /proc/cpuinfo | grep -i tdx || echo "TDX info not in cpuinfo"
ls -la /dev/tdx* 2>/dev/null || echo "TDX devices not found - checking..."

# Install Intel SGX/TDX software stack
wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | sudo apt-key add -
echo "deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu jammy main" | sudo tee /etc/apt/sources.list.d/intel-sgx.list

sudo apt-get update
sudo apt-get install -y \
    libsgx-urts \
    libsgx-uae-service \
    libsgx-quote-ex \
    libtdx-attest \
    tdx-qgs \
    sgx-ra-service

# 3. Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv ~/llm_env
source ~/llm_env/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install PyTorch with CPU optimizations (Intel MKL)
echo "Installing PyTorch with Intel MKL..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 5. Install HuggingFace Transformers and related packages
echo "Installing HuggingFace Transformers..."
pip install transformers accelerate sentencepiece protobuf

# 6. Install additional ML libraries
echo "Installing additional ML libraries..."
pip install \
    numpy \
    scipy \
    scikit-learn \
    datasets \
    evaluate \
    wandb

# 7. Install llama.cpp for CPU-optimized inference
echo "Building llama.cpp..."
cd ~
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with OpenBLAS and OpenMP for better CPU performance
make clean
make -j$(nproc) LLAMA_OPENBLAS=1 LLAMA_OPENMP=1

# 8. Install vLLM (CPU support)
echo "Installing vLLM CPU version..."
pip install vllm --extra-index-url https://download.pytorch.org/whl/cpu

# 9. Create directories for models and benchmarks
mkdir -p ~/models ~/benchmarks ~/results

echo "=== Python Environment Setup Complete ==="
echo ""
echo "To activate the environment, run: source ~/llm_env/bin/activate"
echo "llama.cpp built at: ~/llama.cpp"
echo "Models directory: ~/models"
echo "Benchmarks directory: ~/benchmarks"
