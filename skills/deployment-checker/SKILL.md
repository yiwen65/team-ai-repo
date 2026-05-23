---
name: apollo-deployment-checker
description: >
  Apollo-Lite 自动驾驶系统部署深度助手。覆盖 Docker 容器化（whl 工具链）、Bazel 构建系统、
  cyber 运行时环境、模型部署（TensorRT/ONNX）、OTA 升级（A/B 分区）、系统诊断（cyber_monitor/cyber_recorder）。
  在以下场景触发使用：
  (1) Apollo-lite 开发环境搭建（Docker/whl/Bazel），(2) 部署后问题排查（cyber 启动失败/DAG 加载失败/模块崩溃），
  (3) Docker 镜像构建与优化（multi-stage/ layer cache），(4) 模型转换与部署（Caffe/ONNX → TensorRT），
  (5) cyber_recorder 数据录制与回放问题，(6) OTA 包生成与验证，(7) 系统资源监控与性能诊断。
---

# Apollo Deployment Checker

Apollo-Lite 系统部署深度助手。覆盖 Docker/whl/Bazel/cyber/TensorRT/OTA 全链路。

## 快速启动

用户提供以下信息即可触发分析：
- 部署目标（开发机/测试车/量产车）+ 硬件配置
- 问题描述（启动失败/构建错误/模型加载失败/OTA 失败）+ 日志
- whl/Docker/Bazel 配置 + cyber 状态
- OTA 包或模型文件

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| Docker/whl | 容器化部署、whl 命令行工具、环境配置 | `references/docker-whl.md` |
| Bazel 构建 | 构建系统、依赖管理、编译优化、缓存 | `references/bazel-build.md` |
| Cyber 运行时 | cyber 启动、DAG 加载、模块生命周期 | `references/cyber-runtime.md` |
| 模型部署 | Caffe/ONNX → TensorRT、精度验证 | `references/model-deployment.md` |
| OTA 升级 | A/B 分区、差分包、回滚、版本管理 | `references/ota-upgrade.md` |
| 系统诊断 | cyber_monitor、资源监控、日志分析 | `references/system-diagnostics.md` |

## whl 工具链

```bash
# 主机环境配置
sudo bash docker/setup_host/setup_host.sh

# 启动开发容器
whl start

# 进入容器
whl enter

# 停止容器
whl stop

# 查看容器状态
whl status
```

## Docker 配置

```bash
# .env.global 环境变量
DEV_USE_GPU=true
DEV_BAZEL_CACHE_DIR=/apollo/.cache/bazel

# 生成的环境文件
docker/.env.dev.local
docker/.env.test.local
docker/.env.prod.local
```

## Bazel 构建命令

```bash
# 构建全部模块
bazel build //modules/...

# 构建指定模块
bazel build //modules/perception:all

# 调试构建
bazel build -c dbg //modules/planning:libplanning_component.so

# 优化构建
bazel build -c opt //modules/control:libcontrol_component.so

# 运行测试
bazel test //modules/planning/integration_tests:all

# 清理缓存
bazel clean
```

## Cyber 启动流程

```bash
# 启动 cyber 主进程
cyber_launch start modules/planning/launch/planning.launch

# 停止
cyber_launch stop modules/planning/launch/planning.launch

# 查看所有模块状态
cyber_launch status

# 启动单个 DAG
cyber_launch start modules/planning/dag/planning.dag
```

## 模型部署

```bash
# Caffe → ONNX
caffe2onnx \
  --prototxt model.prototxt \
  --caffemodel model.caffemodel \
  --output model.onnx

# ONNX → TensorRT
trtexec \
  --onnx=model.onnx \
  --saveEngine=model.trt \
  --fp16 \
  --workspace=4096
```

## 系统诊断命令

```bash
# 查看所有 channel
cyber_channel list

# 查看 channel 详情
cyber_channel info /apollo/perception/obstacles

# 监听 channel 数据
cyber_channel echo /apollo/perception/obstacles

# 录制数据
cyber_recorder record -a

# 回放数据
cyber_recorder play -f record_file.record

# 查看系统资源
cyber_monitor

# 查看节点状态
cyber_node list
cyber_node info /perception
```

## OTA 升级

```bash
# OTA 包结构
ota_package/
├── MANIFEST.json       # 版本信息、兼容性
├── system.img          # 系统镜像
├── models/             # 模型文件
├── configs/            # 配置文件
└── scripts/
    ├── pre_install.sh  # 安装前脚本
    ├── post_install.sh # 安装后脚本
    └── verify.sh       # 验证脚本

# 车端 OTA 流程
1. 下载 OTA 包
2. 校验签名和哈希
3. 写入备用分区（B 分区）
4. 切换启动分区
5. 重启并验证
6. 失败则回滚到 A 分区
```

## 输出规范

```markdown
# Apollo 部署检查报告

## 1. 环境基线快照
## 2. Docker/whl 状态
## 3. Bazel 构建状态
## 4. Cyber 运行时状态
## 5. 模型部署状态
## 6. 系统资源监控
## 7. 问题根因
## 8. 修复方案
```

## 关键原则

- **whl 必须先 setup_host**：`setup_host.sh` 配置 Docker、NVIDIA runtime、udev 规则
- **Bazel 构建必须锁定版本**：`.bazelversion` 文件确保构建一致性
- **cyber 启动先查 DAG 配置**：class_name 不匹配、so 路径错误是常见启动失败原因
- **模型部署必须验证精度**：Caffe → TensorRT 后，用 500+ 样本验证 mAP 掉点 < 0.5%
- **OTA 必须有回滚机制**：A/B 分区 + 启动验证 + 失败自动回滚
- **系统监控必须覆盖全链路**：CPU/内存/磁盘 + 模块心跳 + 消息延迟
