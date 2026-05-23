# 模型部署参考

## ONNX → TensorRT 流程

```bash
# 1. 导出 ONNX
python export_onnx.py --weights model.pt --input-size 640 640

# 2. ONNX → TensorRT
trtexec \
  --onnx=model.onnx \
  --saveEngine=model.engine \
  --fp16 \
  --int8 \
  --workspace=4096 \
  --minShapes=input:1x3x640x640 \
  --optShapes=input:8x3x640x640 \
  --maxShapes=input:16x3x640x640

# 3. 精度验证
python validate_trt.py --engine model.engine --dataset val/
```

## 量化策略

| 精度 | 速度提升 | mAP 损失 | 适用 |
|------|---------|---------|------|
| FP32 | 1x | 0% | 基准 |
| FP16 | 1.5-2x | < 0.1% | 通用 |
| INT8 | 2-3x | 0.5-2% | 部署 |
| INT8 + DLA | 3-4x | 1-3% | Orin DLA |

**敏感层保留 FP16**：
- Deformable Convolution
- Attention（Softmax）
- NMS / SoftNMS
- 深度估计分支

## ONNX Runtime 部署

```cpp
#include <onnxruntime_cxx_api.h>

Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "autoware");
Ort::SessionOptions session_options;
session_options.SetIntraOpNumThreads(4);
session_options.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);

Ort::Session session(env, "model.onnx", session_options);

// 输入/输出绑定
std::vector<const char*> input_names = {"images"};
std::vector<const char*> output_names = {"output0"};
```

## 常见问题

| 问题 | 根因 | 修复 |
|------|------|------|
| `Could not find implementation` | 算子不支持 | 自定义 plugin 或改模型 |
| 精度掉点大 | 校准数据分布不匹配 | 增加校准样本数（500+） |
| 推理延迟不稳定 | 动态 shape / 内存分配 | 固定 max shape，预分配 |
| DLA 不支持 | 部分算子 DLA 不支持 | 回退到 GPU |
