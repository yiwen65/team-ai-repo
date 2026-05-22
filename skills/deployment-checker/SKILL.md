# Deployment Checker

## Description

部署检查助手 - 验证自动驾驶系统部署配置，排查常见问题。

## When to Use

- 部署前配置检查
- 部署后问题排查
- 环境一致性验证
- CI/CD 流程检查

## How to Use

1. 描述部署环境（ROS版本、Ubuntu版本、硬件配置）
2. 提供配置文件或日志
3. 描述遇到的问题

## Examples

### 例1：部署前检查
```
环境：
- Ubuntu 20.04
- ROS2 Galactic
- CUDA 11.4
- 目标：部署 Autoware Universe

请生成部署检查清单。
```

### 例2：问题排查
```
错误日志：
[ERROR] [lidar_driver]: Failed to open port /dev/ttyUSB0

请分析可能原因和解决方案。
```

## Checklist Template

- [ ] 系统依赖检查
- [ ] ROS环境检查
- [ ] 驱动安装检查
- [ ] 网络配置检查
- [ ] 权限配置检查
- [ ] 启动文件检查
- [ ] 日志系统检查

## Common Issues

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 端口无权限 | 用户不在dialout组 | `sudo usermod -a -G dialout $USER` |
| ROS节点启动失败 | 依赖未安装 | `rosdep install --from-paths src` |
| CUDA版本不匹配 | 驱动与runtime不一致 | 重新安装对应版本 |

## Notes

- 始终先检查日志级别设置
- 使用 `ros2 doctor` 进行基础诊断
- 记录所有配置变更到版本控制
