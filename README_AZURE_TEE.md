# Azure TEE机密计算实例部署指南

本文档描述了在Azure上部署Intel TDX机密计算实例（Standard_DC8s_v3）并运行Llama2基准测试的完整流程。

## 概述

此项目完成了以下任务：
1. ✅ 安装Azure CLI
2. ✅ 创建资源组 `satisficing-rg`
3. ✅ 部署Standard_DC8s_v3机密VM（Intel TDX）
4. ✅ 安装Python环境和大模型推理框架
5. ✅ 运行Llama2基准测试验证TEE性能损失<10%

## 环境要求

- Azure订阅（支持机密计算）
- Azure CLI 2.40+
- SSH客户端
- Python 3.8+

## 文件说明

| 文件 | 说明 |
|------|------|
| `azure_tee_deploy.sh` | Azure VM部署脚本 |
| `setup_tee_env.sh` | Python环境和推理框架安装脚本 |
| `run_llama2_benchmark.sh` | Llama2基准测试脚本 |
| `analyze_tee_performance.py` | TEE性能分析脚本 |

## 快速开始

### 步骤1: 登录Azure

```bash
# 交互式登录
az login

# 或使用服务主体（自动化场景）
az login --service-principal \
    -u $AZURE_CLIENT_ID \
    -p $AZURE_CLIENT_SECRET \
    --tenant $AZURE_TENANT_ID
```

### 步骤2: 部署TEE VM

```bash
chmod +x azure_tee_deploy.sh
./azure_tee_deploy.sh
```

部署完成后，脚本会输出：
- 资源组名称
- VM名称和大小
- 公网IP地址
- SSH连接命令

### 步骤3: 配置Python环境

SSH连接到VM后：

```bash
chmod +x setup_tee_env.sh
./setup_tee_env.sh
```

这将安装：
- Python 3.12虚拟环境
- PyTorch (CPU版本，带Intel MKL优化)
- HuggingFace Transformers
- llama.cpp (CPU优化版本)
- Intel SGX/TDX工具

### 步骤4: 运行基准测试

```bash
chmod +x run_llama2_benchmark.sh
./run_llama2_benchmark.sh
```

测试包括：
- HuggingFace Transformers推理性能
- llama.cpp CPU推理性能
- 内存带宽测试
- 系统信息收集

### 步骤5: 分析性能

```bash
python3 analyze_tee_performance.py ~/results/benchmark_*.txt
```

## 技术细节

### VM规格: Standard_DC8s_v3

| 属性 | 规格 |
|------|------|
| vCPU | 8 |
| 内存 | 32 GB |
| 机密内存 | 32 GB (TDX) |
| 临时存储 | 200 GB |
| 安全类型 | ConfidentialVM |
| TEE技术 | Intel TDX |

### 性能基线

参考的非TEE环境 (Standard_D8s_v3):
- Llama2-7B推理: ~8.5 tokens/sec
- 内存带宽: ~25 GB/s
- 模型加载时间: ~45秒

### 性能阈值

目标：TEE开销 < 10%

| 指标 | 基线 | TEE目标 |
|------|------|---------|
| 推理吞吐量 | 8.5 t/s | > 7.65 t/s |
| 内存带宽 | 25 GB/s | > 22.5 GB/s |
| 加载时间 | 45 s | < 49.5 s |

## 已知限制

1. **Azure订阅限制**: 需要预先申请DCsv3系列配额
2. **区域可用性**: DC8s_v3仅在特定区域可用（如eastus, westeurope）
3. **模型下载**: 首次运行需要下载~13GB的Llama2模型
4. **认证**: 需要HuggingFace认证才能下载Llama2模型

## 故障排除

### TDX设备未找到
如果`/dev/tdx*`不存在，可能是因为：
- VM未正确配置为ConfidentialVM
- 主机不支持TDX（检查区域和VM大小）
- 需要重启VM

### 性能低于预期
- 检查CPU频率：`cat /proc/cpuinfo | grep MHz`
- 确认Intel MKL已启用：`python -c "import torch; print(torch.__config__.show())"`
- 检查NUMA绑定：`numactl --hardware`

### 模型下载失败
```bash
# 手动设置HuggingFace Token
export HUGGINGFACE_TOKEN="your_token_here"
huggingface-cli login --token $HUGGINGFACE_TOKEN
```

## 验证清单

部署完成后，确认以下项目：

- [ ] Azure CLI已安装 (`az --version`)
- [ ] 资源组 `satisficing-rg` 已创建
- [ ] VM `tee-vm-dc8sv3` 运行中
- [ ] TDX设备存在 (`ls /dev/tdx*`)
- [ ] Python虚拟环境可用
- [ ] Llama2模型已下载
- [ ] 基准测试完成
- [ ] 性能开销 < 10%

## 结果汇报

部署成功后，收集以下信息汇报：

```bash
# 获取VM信息
az vm show --resource-group satisficing-rg --name tee-vm-dc8sv3

# 获取IP地址
az network public-ip show \
    --resource-group satisficing-rg \
    --name tee-vm-dc8sv3-pip \
    --query ipAddress \
    --output tsv

# 获取基准测试结果
cat ~/results/benchmark_*.txt
```

## 参考链接

- [Azure 机密计算文档](https://docs.microsoft.com/azure/confidential-computing/)
- [Intel TDX概述](https://www.intel.com/content/www/us/en/developer/tools/trust-domain-extensions/overview.html)
- [Llama2模型](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)

## 许可证

此项目用于测试和评估目的。
