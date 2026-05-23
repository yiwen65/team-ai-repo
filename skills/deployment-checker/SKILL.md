---
name: deployment-checker
description: >
  自动驾驶系统部署深度助手。覆盖 ROS2 环境搭建（Galactic/Humble/Iron）、依赖管理（rosdep/vcpkg/conan）、
  容器化部署（Docker/NVIDIA Container）、模型部署（TensorRT/ONNX Runtime）、
  OTA 升级（A/B 分区/差分/回滚）、诊断与监控（ros2 doctor/systemd/ELK）、
  CI/CD 流水线（GitLab CI/Jenkins/GitHub Actions）、现场问题排查（日志分析/core dump/性能 profiling）。
  在以下场景触发使用：
  (1) 新环境部署前检查清单生成与执行，(2) 部署后问题排查（节点启动失败/话题无数据/性能不达标），
  (3) Docker 镜像构建与优化（层缓存/多阶段/基础镜像选型），(4) 模型转换与部署（ONNX → TensorRT/ORT），
  (5) OTA 包生成与验证，(6) 现场日志分析与 core dump 调试，(7) CI/CD 流水线设计与故障排查。
---

# Deployment Checker

自动驾驶系统部署深度助手。覆盖环境搭建、容器化、OTA、诊断监控、CI/CD 全链路。

## 快速启动

用户提供以下信息即可触发分析：
- 部署目标（开发机/测试车/量产车/云端）+ 硬件配置
- 问题描述（启动失败/性能差/OTA失败/监控告警）+ 日志
- 部署产物（Dockerfile/docker-compose/OTA包/模型文件）
- CI/CD 配置（.gitlab-ci.yml/Jenkinsfile/GitHub Actions）

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| ROS2 环境 | 版本选择、依赖安装、workspace 构建 | `references/ros2-setup.md` |
| 容器化 | Docker、NVIDIA Container、多阶段构建 | `references/containerization.md` |
| 模型部署 | ONNX → TensorRT/ORT、量化、plugin | `references/model-deployment.md` |
| OTA | A/B 分区、差分包、回滚、版本管理 | `references/ota.md` |
| 诊断监控 | ros2 doctor、systemd、日志、告警 | `references/diagnostics.md` |
| CI/CD | 流水线设计、缓存、并行、产物管理 | `references/cicd.md` |

## 部署检查流程

1. **环境基线** → OS 版本、内核、CUDA、驱动、ROS2 版本
2. **依赖检查** → rosdep、vcpkg、apt、pip、conan
3. **构建检查** → colcon、CMake 选项、编译器版本
4. **运行时检查** → 节点启动、话题连通、参数加载、性能达标
5. **容器检查** → 镜像大小、层缓存、GPU 访问、安全扫描
6. **OTA 检查** → 包完整性、签名验证、兼容性、回滚测试
7. **监控检查** → 日志收集、指标上报、告警规则、Dashboard

## 工具脚本

| 脚本 | 用途 |
|---|---|
| `scripts/ros2_health_check.sh` | 全面检查 ROS2 环境健康状态 |
| `scripts/docker_size_analyzer.py` | 分析 Docker 镜像层大小，定位膨胀原因 |
| `scripts/ota_verifier.py` | 验证 OTA 包完整性、签名、兼容性 |
| `scripts/log_analyzer.py` | 解析 ROS2/系统日志，定位错误根因 |

## 输出规范

```markdown
# 部署检查报告

## 1. 环境基线快照
## 2. 检查项结果（通过/失败/警告）
| 检查项 | 状态 | 详情 | 修复建议 |
|--------|------|------|----------|
| ... | ✅/❌/⚠️ | ... | ... |

## 3. 严重问题（BLOCKER）
## 4. 警告项（WARNING）
## 5. 优化建议
## 6. 部署验证清单
```

## 关键原则

- **部署环境必须版本锁定**：OS + CUDA + ROS2 + 依赖库的版本必须记录在案，禁止"最新版"
- **Docker 镜像必须多阶段构建**：builder 阶段装依赖 + 编译，runtime 阶段只拷产物，镜像大小减少 60%+
- **模型部署必须验证精度**：ONNX → TensorRT 后，用 500+ 样本验证 mAP 掉点 < 0.5%
- **OTA 必须有回滚机制**：A/B 分区 + 启动验证 + 失败自动回滚，不允许变砖
- **生产日志必须结构化**：JSON 格式 + 统一 trace_id + 可检索，禁止 `printf` 自由文本
