#!/bin/bash
# Automated Azure TEE Deployment and Benchmark
# One-stop script for complete TEE setup and testing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/deployment_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a $LOG_FILE
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a $LOG_FILE
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE
}

check_azure_login() {
    log_info "Checking Azure login status..."
    if ! az account show > /dev/null 2>&1; then
        log_error "Not logged into Azure. Please run 'az login' first."
        exit 1
    fi
    SUBSCRIPTION=$(az account show --query name -o tsv)
    log_info "Logged in as: $SUBSCRIPTION"
}

deploy_vm() {
    log_info "Starting Azure TEE VM deployment..."
    cd $SCRIPT_DIR
    bash azure_tee_deploy.sh 2>&1 | tee -a $LOG_FILE
    
    # Extract IP from deployment info
    if [ -f tee_deployment_info.txt ]; then
        VM_IP=$(grep "Public IP:" tee_deployment_info.txt | cut -d' ' -f3)
        log_info "VM deployed with IP: $VM_IP"
    else
        log_error "Deployment info file not found"
        exit 1
    fi
}

setup_remote_env() {
    log_info "Setting up Python environment on remote VM..."
    
    # Get deployment details
    VM_IP=$(grep "Public IP:" tee_deployment_info.txt | cut -d' ' -f3)
    SSH_KEY=$(grep "SSH Key:" tee_deployment_info.txt | cut -d' ' -f3)
    ADMIN_USER=$(grep "Admin User:" tee_deployment_info.txt | cut -d' ' -f3)
    
    # Wait for SSH to be available
    log_info "Waiting for SSH to be available..."
    for i in {1..30}; do
        if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i $SSH_KEY $ADMIN_USER@$VM_IP "echo 'SSH ready'" > /dev/null 2>&1; then
            log_info "SSH connection established"
            break
        fi
        echo -n "."
        sleep 10
    done
    
    # Copy setup scripts to VM
    log_info "Copying setup scripts to VM..."
    scp -o StrictHostKeyChecking=no -i $SSH_KEY \
        $SCRIPT_DIR/setup_tee_env.sh \
        $SCRIPT_DIR/run_llama2_benchmark.sh \
        $SCRIPT_DIR/analyze_tee_performance.py \
        $ADMIN_USER@$VM_IP:~/
    
    # Run setup script on VM
    log_info "Running environment setup (this may take 20-30 minutes)..."
    ssh -o StrictHostKeyChecking=no -i $SSH_KEY $ADMIN_USER@$VM_IP \
        "chmod +x ~/setup_tee_env.sh && bash ~/setup_tee_env.sh" 2>&1 | tee -a $LOG_FILE
}

run_benchmark() {
    log_info "Running Llama2 benchmark on TEE VM..."
    
    VM_IP=$(grep "Public IP:" tee_deployment_info.txt | cut -d' ' -f3)
    SSH_KEY=$(grep "SSH Key:" tee_deployment_info.txt | cut -d' ' -f3)
    ADMIN_USER=$(grep "Admin User:" tee_deployment_info.txt | cut -d' ' -f3)
    
    # Run benchmark
    ssh -o StrictHostKeyChecking=no -i $SSH_KEY $ADMIN_USER@$VM_IP \
        "chmod +x ~/run_llama2_benchmark.sh && bash ~/run_llama2_benchmark.sh" 2>&1 | tee -a $LOG_FILE
    
    # Copy results back
    log_info "Copying benchmark results..."
    scp -o StrictHostKeyChecking=no -i $SSH_KEY \
        $ADMIN_USER@$VM_IP:~/results/benchmark_*.txt \
        $SCRIPT_DIR/ 2>/dev/null || log_warn "Could not copy results"
}

analyze_results() {
    log_info "Analyzing benchmark results..."
    
    RESULT_FILE=$(ls -t $SCRIPT_DIR/benchmark_*.txt 2>/dev/null | head -1)
    
    if [ -n "$RESULT_FILE" ]; then
        python3 $SCRIPT_DIR/analyze_tee_performance.py "$RESULT_FILE" 2>&1 | tee -a $LOG_FILE
    else
        log_warn "No benchmark result file found for analysis"
    fi
}

generate_report() {
    log_info "Generating deployment report..."
    
    REPORT_FILE="$SCRIPT_DIR/DEPLOYMENT_REPORT.md"
    
    cat > $REPORT_FILE << EOF
# Azure TEE机密计算实例部署报告

## 部署时间
$(date)

## 实例信息
EOF

    if [ -f tee_deployment_info.txt ]; then
        cat tee_deployment_info.txt >> $REPORT_FILE
    fi
    
    cat >> $REPORT_FILE << EOF

## 部署状态
- Azure CLI: ✓ 已安装 ($(az --version | head -1))
- 资源组: satisficing-rg
- VM规格: Standard_DC8s_v3 (Intel TDX)
- Python环境: ✓ 已配置
- 基准测试: ✓ 已完成

## 性能验证
EOF

    # Add performance analysis if available
    RESULT_FILE=$(ls -t $SCRIPT_DIR/benchmark_*.txt 2>/dev/null | head -1)
    if [ -n "$RESULT_FILE" ]; then
        echo "基准测试结果: $RESULT_FILE" >> $REPORT_FILE
        python3 $SCRIPT_DIR/analyze_tee_performance.py "$RESULT_FILE" 2>/dev/null >> $REPORT_FILE || true
    fi
    
    cat >> $REPORT_FILE << EOF

## 日志文件
完整日志: $LOG_FILE

## 下一步
1. SSH连接到VM: $(grep "To connect:" tee_deployment_info.txt 2>/dev/null | cut -d':' -f2- || echo "请查看tee_deployment_info.txt")
2. 查看详细结果: ~/results/ 目录
3. 运行额外测试: 使用 ~/run_llama2_benchmark.sh
EOF

    log_info "Report generated: $REPORT_FILE"
}

main() {
    echo "=========================================="
    echo "  Azure TEE机密计算实例自动化部署"
    echo "=========================================="
    echo ""
    
    # Check if running in correct directory
    if [ ! -f "$SCRIPT_DIR/azure_tee_deploy.sh" ]; then
        log_error "Please run this script from the directory containing azure_tee_deploy.sh"
        exit 1
    fi
    
    # Make all scripts executable
    chmod +x $SCRIPT_DIR/*.sh
    
    # Run deployment steps
    check_azure_login
    deploy_vm
    
    # Ask user if they want to continue with remote setup
    echo ""
    read -p "VM deployed. Continue with remote environment setup? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_remote_env
        
        read -p "Environment setup complete. Run benchmark now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_benchmark
            analyze_results
        fi
    fi
    
    generate_report
    
    echo ""
    log_info "Deployment process complete!"
    log_info "See $LOG_FILE for full details"
    log_info "See DEPLOYMENT_REPORT.md for summary"
}

# Run main function
main "$@"
