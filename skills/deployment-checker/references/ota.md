# OTA 升级参考

## A/B 分区方案

```
系统分区布局：
  ├── Boot Partition (A/B)
  ├── Rootfs Partition A (当前运行)
  ├── Rootfs Partition B (升级目标)
  ├── Data Partition (共享，不覆盖)
  └── Recovery Partition (救援)

升级流程：
  1. 下载 OTA 包到 Data Partition
  2. 校验签名和哈希
  3. 写入 Rootfs B
  4. 设置 Boot 标志指向 B
  5. 重启
  6. 启动自检（health check）
  7. 自检通过 → 完成
  8. 自检失败 → 回滚到 A
```

## OTA 包格式

```
ota_package.zip
  ├── MANIFEST.json       # 版本信息、兼容性、签名
  ├── system.img          # 根文件系统（差分或全量）
  ├── models/             # 模型文件
  ├── configs/            # 配置文件
  ├── scripts/
  │   ├── pre_install.sh  # 升级前脚本
  │   ├── post_install.sh # 升级后脚本
  │   └── verify.sh       # 验证脚本
  └── signature.sig       # 数字签名
```

## 差分生成

```bash
# 生成差分包
bsdiff old_system.img new_system.img patch.bin

# 车端应用
bspatch old_system.img new_system.img patch.bin
```

**差分策略**：
- 大文件（system.img）：bsdiff，减少 70-90%
- 模型文件：全量替换（模型格式不易差分）
- 配置文件：文本 diff，最小化

## 回滚机制

```cpp
bool verifySystem() {
    // 启动自检
    if (!checkROS2Nodes()) return false;
    if (!checkSensorTopics()) return false;
    if (!checkPerformanceMetrics()) return false;
    if (!checkSafetyMonitors()) return false;
    return true;
}

void afterBoot() {
    if (!verifySystem()) {
        logError("System verification failed, rolling back...");
        switchBootPartition();  // 切回 A
        reboot();
    }
}
```

## 安全要求

- **签名验证**：OTA 包必须 RSA/ECDSA 签名验证
- **降级保护**：版本号必须递增，禁止降级（防回滚攻击）
- **完整性校验**：SHA256 校验所有文件
- **加密传输**：HTTPS + 证书固定（pinning）
