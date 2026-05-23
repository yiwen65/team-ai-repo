# 容器化部署参考

## Dockerfile 最佳实践

```dockerfile
# 多阶段构建示例
FROM nvcr.io/nvidia/cuda:11.8-devel-ubuntu22.04 AS builder

# 安装依赖
RUN apt-get update && apt-get install -y \
    python3-pip cmake libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# 编译阶段
COPY src/ /workspace/src/
WORKDIR /workspace
RUN rosdep install --from-paths src --ignore-src -y \
    && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# Runtime 阶段（最小化）
FROM nvcr.io/nvidia/cuda:11.8-runtime-ubuntu22.04

# 只安装运行时依赖
RUN apt-get update && apt-get install -y \
    libopencv-core4.5d \
    && rm -rf /var/lib/apt/lists/*

# 拷贝产物
COPY --from=builder /workspace/install/ /opt/autoware/

# 环境变量
ENV ROS_DISTRO=humble
ENV LD_LIBRARY_PATH=/opt/autoware/lib:$LD_LIBRARY_PATH

ENTRYPOINT ["/opt/autoware/setup.bash"]
```

## 镜像优化

| 优化项 | 方法 | 效果 |
|--------|------|------|
| 多阶段构建 | builder + runtime | 减少 60%+ |
| 层缓存 | 依赖先于源码 COPY | 加速重建 |
| .dockerignore | 排除 .git/build/log | 减少上下文 |
| 合并 RUN | `apt &&` 单条 | 减少层数 |
| 基础镜像 | runtime 替代 devel | 减少 50% |

## NVIDIA Container Toolkit

```bash
# 安装
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 运行带 GPU 的容器
docker run --gpus all -it --rm autoware:latest
```

**常见问题**：
- `docker: Error response from daemon: could not select device driver` → nvidia-container-toolkit 未安装
- `CUDA out of memory` → 多进程竞争 GPU，限制 `CUDA_VISIBLE_DEVICES`
