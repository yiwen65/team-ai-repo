# Python 数据管线审查参考

## GIL（全局解释器锁）

**问题**：Python 多线程无法真正并行 CPU 密集型任务

**解决方案**：
- 数据处理用 `multiprocessing` 或 `concurrent.futures.ProcessPoolExecutor`
- NumPy 操作释放 GIL（`np.dot` 等 C 实现）
- I/O 密集型用 `asyncio` 或 `ThreadPoolExecutor`

## 内存管理

| 问题 | 症状 | 修复 |
|------|------|------|
| 循环引用 | 内存不释放 | `weakref` 或手动断开引用 |
| 大对象拷贝 | 内存峰值高 | `numpy` view 而非 copy |
| 生成器未消费 | 内存泄漏 | 确保 `for x in gen():` 遍历完 |
| Pandas chain | 中间 DataFrame 堆积 | 用 `pipe` 或 `inplace=True` |

## 类型安全

```python
# 推荐：使用类型注解 + mypy
from typing import List, Tuple, Optional
import numpy as np

def process_pointcloud(
    points: np.ndarray,  # shape: (N, 4) [x, y, z, intensity]
    roi: Tuple[float, float, float, float]  # (x_min, x_max, y_min, y_max)
) -> Optional[np.ndarray]:
    mask = (
        (points[:, 0] >= roi[0]) & (points[:, 0] <= roi[1]) &
        (points[:, 1] >= roi[2]) & (points[:, 1] <= roi[3])
    )
    filtered = points[mask]
    return filtered if len(filtered) > 0 else None
```

## 数据管线常见模式

```python
# 推荐：链式处理，每步可插拔
pipeline = [
    LoadData(),
    Preprocess(resolution=0.1),
    Filter(roi=(-50, 50, -30, 30)),
    Voxelize(voxel_size=0.2),
    Save(output_dir="./processed")
]

for step in pipeline:
    data = step(data)
```

## 审查要点

- [ ] 大文件读取是否使用 `mmap` 或流式读取
- [ ] 多进程是否正确使用 `if __name__ == "__main__"` 保护
- [ ] `pandas`/`numpy` 操作是否避免不必要的拷贝
- [ ] 异常处理是否覆盖 I/O 错误和数据格式错误
- [ ] 日志是否使用 `logging` 模块而非 `print`
