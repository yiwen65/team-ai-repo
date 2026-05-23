# 检测算法参考

## 算法选型决策树

```
算力充足 (>= 200 TOPS) + 城市场景复杂
  → BEVFusion / UniAD / SparseDrive

算力中等 (50-100 TOPS) + 高速/快速路
  → BEVDet / CenterPoint / PointPillars + 相机后融合

算力有限 (<= 30 TOPS) + 高速场景
  → YOLOv8-3D / PointPillars / 纯视觉 BEV

纯视觉 + 低成本
  → BEVDet / LSS / BEVFormer（轻量版）
```

## 关键模型对比

| 模型 | 模态 | 3D mAP (nuScenes) | 速度 (FPS, Orin) | 显存 |
|-----|------|------------------|-----------------|------|
| BEVFusion | C+L | 70.2 | ~8 | ~12GB |
| CenterPoint | L | 60.3 | ~15 | ~6GB |
| PointPillars | L | 49.9 | ~25 | ~4GB |
| BEVDet | C | 31.2 | ~12 | ~8GB |
| DETR3D | C | 41.2 | ~10 | ~10GB |

## 部署注意事项

- **TensorRT 8.6+** 支持 `IPluginV2DynamicExt` 自定义插件，但 BEVPool / Voxelization 需手写 CUDA
- **量化策略**：主干网络 INT8，BEV Encoder 和 DeformAttn 保留 FP16
- **Orin 平台**：使用 `trtexec --fp16 --int8` 并开启 DLA 卸载（支持层有限，需验证）
