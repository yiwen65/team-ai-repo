# Apollo 感知部署参考

## Bazel 构建

Apollo-lite 使用 Bazel 构建系统：

```bash
# 构建感知模块
bazel build //modules/perception:libperception_component.so

# 构建所有感知子模块
bazel build //modules/perception/...

# 调试构建
bazel build -c dbg //modules/perception:camera_perception

# 优化构建
bazel build -c opt //modules/perception:camera_perception
```

### BUILD 文件示例

```python
# modules/perception/camera/app/BUILD
cc_library(
    name = "camera_perception_component",
    srcs = ["camera_perception_component.cc"],
    hdrs = ["camera_perception_component.h"],
    deps = [
        "//cyber",
        "//modules/common_msgs:sensor_msgs",
        "//modules/perception/camera/lib:detector",
        "//modules/perception/camera/lib:tracker",
    ],
    linkshared = True,
)
```

## TensorRT 部署

### 模型转换

```bash
# Caffe → ONNX
caffe2onnx \
  --prototxt yolo-3d.prototxt \
  --caffemodel yolo-3d.caffemodel \
  --output yolo-3d.onnx

# ONNX → TensorRT
trtexec \
  --onnx=yolo-3d.onnx \
  --saveEngine=yolo-3d.trt \
  --fp16 \
  --workspace=4096
```

### TensorRT 配置

```protobuf
// inference 配置
inference_config {
  model_type: TENSORRT
  engine_file: "yolo-3d.trt"
  
  // GPU 配置
  gpu_id: 0
  max_batch_size: 1
  
  // 精度
  precision: FP16
}
```

## Docker 部署

```bash
# 启动开发容器
whl start

# 进入容器
whl enter

# 在容器内构建
bazel build //modules/perception/...
```

## 性能优化

| 优化项 | 方法 | 效果 |
|--------|------|------|
| GPU 批量推理 | 合并多帧 | 延迟 -30% |
| TensorRT FP16 | 半精度 | 延迟 -40%，精度 -0.1% |
| CUDA Stream | 异步传输 | CPU-GPU 并行 |
| Shared Memory | cyber SHM | IPC 延迟 -90% |
| Pipeline 并行 | 多 Component | 吞吐 +50% |

## 常见问题

| 问题 | 根因 | 修复 |
|------|------|------|
| Bazel 编译失败 | 依赖缺失 | `rosdep install` 或手动安装 |
| TensorRT 加载失败 | 版本不匹配 | 重新生成 engine |
| GPU 内存不足 | 模型太大 | 减小 batch_size / 使用 FP16 |
| Docker 内无法访问 GPU | nvidia-runtime 未配置 | `whl` setup_host |
| 模型精度掉点 | 量化损失 | 敏感层保留 FP32 |
