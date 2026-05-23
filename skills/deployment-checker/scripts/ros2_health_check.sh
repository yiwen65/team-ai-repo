#!/bin/bash
# ros2_health_check.sh
# 全面检查 ROS2 环境健康状态

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local cmd="$2"
    local expected="$3"
    
    echo -n "Checking $name... "
    
    if eval "$cmd" >/dev/null 2>&1; then
        if [ -n "$expected" ] && ! eval "$expected" >/dev/null 2>&1; then
            echo -e "${YELLOW}WARN${NC}"
            ((WARN++))
        else
            echo -e "${GREEN}PASS${NC}"
            ((PASS++))
        fi
    else
        echo -e "${RED}FAIL${NC}"
        ((FAIL++))
    fi
}

echo "================================"
echo "ROS2 Health Check"
echo "================================"

# System
check "Ubuntu Version" "lsb_release -a | grep -q 'Ubuntu 22.04'"
check "Kernel Version" "uname -r | awk -F. '{print \$1}' | grep -q '5'"

# ROS2
check "ROS2 Installed" "command -v ros2"
check "ROS2 Environment" "[ -n \"$ROS_DISTRO\" ]"
check "ros2 doctor" "ros2 doctor"

# CUDA / GPU
check "NVIDIA Driver" "nvidia-smi"
check "CUDA Runtime" "nvcc --version"
check "CUDA Environment" "[ -n \"$CUDA_HOME\" ] || [ -n \"/usr/local/cuda\" ]"

# DDS
check "DDS Middleware" "[ -n \"$RMW_IMPLEMENTATION\" ] || true"
check "Domain ID" "[ -n \"$ROS_DOMAIN_ID\" ] || true"

# Python
check "Python3" "python3 --version"
check "rosdep" "command -v rosdep"

# Build tools
check "colcon" "command -v colcon"
check "cmake" "cmake --version"
check "gcc" "gcc --version"

echo ""
echo "================================"
echo "Summary: $PASS passed, $FAIL failed, $WARN warnings"
echo "================================"

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}CRITICAL: $FAIL checks failed${NC}"
    exit 1
elif [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}WARNING: $WARN checks with warnings${NC}"
    exit 0
else
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
fi
