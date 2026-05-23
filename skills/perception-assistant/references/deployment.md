# 部署优化参考

## TensorRT 优化流程

1. **ONNX 导出**：确认动态 batch/动态 shape 支持
2. **Plugin 开发**：BEVPool、Voxelization、NMS 需自定义 CUDA plugin
3. **精度校准**：使用 500-1000 张代表性样本做 INT8 calibration
4. **性能分析**：`trtexec --dumpProfile` 定位瓶颈 layer
5. **DLA 卸载**：将 ResNet 主干部分层卸载到 DLA，释放 GPU

## 量化掉点排查

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| mAP 掉 5%+ | INT8 敏感层（DeformConv、Attention） | 保留 FP16 |
| 小目标全部丢失 | BEV grid 量化分辨率不足 | 增大 grid 或保留 FP16 |
| NMS 后无输出 | INT8 得分截断 | 调整校准数据集分布 |
| 远距离目标偏移 | 深度分支量化损失 | 深度分支单独 FP16 |

## 延迟 profiling 要点

```bash
# TensorRT 推理延迟分解
trttexec --onnx=model.onnx --fp16 --int8 \
  --dumpProfile --dumpLayerTime \
  --workspace=4096 --batch=1
```

关注：
- Preprocessing（CPU 端 resize/normalize）
- H2D 拷贝（相机图像 upload）
- 推理时间（GPU kernel）
- D2H 拷贝（结果 download）
- 后处理（CPU NMS / 坐标转换）
