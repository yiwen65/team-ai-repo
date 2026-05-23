# 性能优化审查参考

## Profiling 工具链

| 工具 | 平台 | 用途 |
|------|------|------|
| perf | Linux | CPU 热点、缓存 miss、分支预测 |
| gprof | Linux | 函数调用图、耗时 |
| Valgrind/Callgrind | Linux | 调用图、缓存模拟 |
| Nsight Systems | NVIDIA | GPU-CPU 时间线 |
| Nsight Compute | NVIDIA | Kernel 详细分析 |
| VTune | Intel | CPU/GPU 综合分析 |

## 缓存优化

**数据布局**：
```cpp
// ❌ 结构数组（Array of Structs）
struct Point { float x, y, z, intensity; };
std::vector<Point> points;  // 处理 x 时加载无用数据

// ✅ 数组结构（Structure of Arrays）
struct PointCloud {
    std::vector<float> x, y, z, intensity;
};
// 处理 x 时连续访问，缓存友好
```

**预取**：
```cpp
// GCC/Clang
__builtin_prefetch(&data[i + 64], 0, 3);  // 预读 64 个元素后
```

## 向量化

**编译器自动向量化条件**：
- 循环边界已知
- 无数据依赖（无 `a[i] = a[i-1] + 1`）
- 内存连续访问
- 无函数调用（或 inline）

```cpp
// ✅ 可向量化
for (int i = 0; i < N; ++i) {
    c[i] = a[i] + b[i];
}

// ❌ 不可向量化（数据依赖）
for (int i = 1; i < N; ++i) {
    a[i] = a[i-1] + 1;
}
```

**手动向量化（AVX2）**：
```cpp
#include <immintrin.h>

// 8 float 并行加
__m256 va = _mm256_load_ps(&a[i]);
__m256 vb = _mm256_load_ps(&b[i]);
__m256 vc = _mm256_add_ps(va, vb);
_mm256_store_ps(&c[i], vc);
```

## 编译优化

**推荐编译选项**：
```bash
# Release 构建
-O3 -march=native -ffast-math -funroll-loops
-fomit-frame-pointer -DNDEBUG

# 向量化报告
-fopt-info-vec-all  # GCC
-Rpass=loop-vectorize  # Clang
```

**注意**：`-ffast-math` 牺牲 IEEE 754 严格性换取性能，科学计算慎用

## 自动驾驶常见瓶颈

| 模块 | 典型瓶颈 | 优化方向 |
|------|---------|---------|
| 点云预处理 |  voxelization | GPU CUDA kernel |
| BEV 特征提取 | 大矩阵乘法 | cuBLAS / TensorRT |
| NMS | 串行比较 | GPU 并行 NMS |
| 坐标转换 | 大量 4x4 矩阵乘 | 批量处理 + SIMD |
| 日志 | 文件 I/O | 异步日志 + 环形缓冲 |
