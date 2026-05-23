# CUDA / 推理优化审查参考

## Kernel 设计原则

**线程网格**：
- 线程数：128 或 256（Warp 大小的整数倍）
- 每个 Block 的寄存器数：< 64（避免占用率下降）
- Shared Memory：< 48KB（防止双 block 无法并发）

**内存访问模式**：
- ✅ 合并访问（Coalesced）：线程 k 访问地址 `base + k * sizeof(T)`
- ❌ 分散访问（Strided）：线程 k 访问地址 `base + k * stride`
- ✅ Shared Memory Bank Conflict 避免：`__shared__ float s[32][33]`（padding）

## TensorRT Plugin 审查

```cpp
// 自定义 Plugin 模板
class MyPlugin : public IPluginV2DynamicExt {
public:
    // 必须实现
    int getNbOutputs() const noexcept override { return 1; }
    DimsExprs getOutputDimensions(...) override { ... }
    size_t getWorkspaceSize(...) const noexcept override { return 0; }
    int enqueue(...) noexcept override {
        // Kernel 启动
        myKernel<<<grid, block, 0, stream>>>(...);
        return 0;
    }
    
    // 序列化/反序列化
    size_t getSerializationSize() const noexcept override { return sizeof(params_); }
    void serialize(void *buffer) const noexcept override {
        memcpy(buffer, &params_, sizeof(params_));
    }
};
```

**审查要点**：
- `enqueue` 中禁止 `cudaMemcpy` H2D/D2H（应在 `configurePlugin` 预分配）
- `getWorkspaceSize` 必须返回准确的设备内存需求
- 序列化大小必须与 `serialize` 实际写入一致

## 常见性能陷阱

| 问题 | 影响 | 检测 | 修复 |
|------|------|------|------|
| 隐式同步 | CPU-GPU 串行 | Nsight Systems | 使用 `cudaStream` + 异步 |
| H2D 在 hot path | 延迟暴增 | Nsight | 双缓冲 + 预加载 |
| Bank Conflict | 带宽减半 | Nsight Compute | Padding / 重排 |
| 寄存器溢出 | 性能骤降 | Nsight Compute | 减少局部变量 |
| Warp Divergence | 利用率下降 | Nsight Compute | 重排数据或拆分 kernel |

## 精度问题

| 症状 | 可能原因 | 修复 |
|------|---------|------|
| 输出全 0 | Kernel 未启动（配置错误） | 检查 grid/block 配置 |
| 结果偏移 | FP16 溢出 | 使用 FP32 累加 |
| 随机错误 | 越界访问 | `cuda-memcheck` / compute-sanitizer |
| 性能抖动 | 资源竞争 | 固定 `cudaStream` 优先级 |
