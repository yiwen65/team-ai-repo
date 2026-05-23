# ROS2 环境搭建参考

## 版本选择

| ROS2 版本 | Ubuntu | 状态 | 推荐 |
|-----------|--------|------|------|
| Galactic | 20.04 | EOL (2022-12) | ❌ 不推荐 |
| Humble | 22.04 | LTS (2027-05) | ✅ 推荐 |
| Iron | 22.04 | 标准支持 (2024-11) | ⚠️ 短期项目 |
| Jazzy | 24.04 | LTS (2029-05) | ✅ 新项目 |

## 安装检查清单

```bash
# 1. 系统基础
lsb_release -a          # Ubuntu 版本
uname -r                # 内核版本（推荐 5.15+）

# 2. CUDA / 驱动
nvidia-smi              # GPU 驱动和 CUDA 版本
nvcc --version          # CUDA 编译器

# 3. ROS2 安装
ros2 doctor             # 基础诊断
ros2 topic list         # 守护进程检查

# 4. 依赖
rosdep install --from-paths src --ignore-src -y  # 自动安装依赖

# 5. 编译
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release
```

## 常见问题

| 问题 | 诊断 | 修复 |
|------|------|------|
| `ros2 topic list` 为空 | DDS 发现失败 | 检查 `ROS_DOMAIN_ID`、防火墙、多网卡绑定 |
| 编译失败 `ament_cmake` | 依赖未安装 | `rosdep install` 或手动安装 |
| 节点启动 `symbol not found` | 库版本不匹配 | `ldd` 检查依赖，统一版本 |
| GPU 推理失败 | CUDA 版本不匹配 | 确保 runtime 和 driver 兼容 |
| 消息类型不匹配 | 自定义消息未编译 | 重新编译消息包，source setup.bash |

## Workspace 管理

```bash
# 推荐目录结构
~/autoware/
  ├── src/          # 源码
  ├── build/        # 编译产物
  ├── install/      # 安装产物
  ├── log/          # 编译日志
  └── .repos        # vcs 导入文件

# 构建优化
colcon build \
  --cmake-args -DCMAKE_BUILD_TYPE=Release \
  --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  --parallel-workers $(nproc)
```
