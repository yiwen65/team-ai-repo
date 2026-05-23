# CI/CD 参考

## GitLab CI 示例

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  ROS_DISTRO: humble
  CUDA_VERSION: 11.8

build:
  stage: build
  image: nvcr.io/nvidia/cuda:${CUDA_VERSION}-devel-ubuntu22.04
  script:
    - apt-get update && rosdep install --from-paths src --ignore-src -y
    - colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - build/
      - install/

unit_test:
  stage: test
  needs: [build]
  script:
    - colcon test --packages-select ${PACKAGES}
    - colcon test-result --verbose

integration_test:
  stage: test
  needs: [build]
  image: autoware:simulation
  script:
    - ros2 launch test_scenarios all_tests.launch.py
  artifacts:
    reports:
      junit: test_results.xml

# 模型转换验证
check_models:
  stage: test
  script:
    - python validate_models.py --models-dir models/
  rules:
    - changes:
        - models/*
        - scripts/validate_models.py

deploy_docker:
  stage: deploy
  needs: [unit_test, integration_test]
  script:
    - docker build -t ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA} .
    - docker push ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA}
  only:
    - main
```

## 缓存策略

| 缓存项 | 策略 | 失效条件 |
|--------|------|---------|
| apt 包 | Docker 层缓存 | Dockerfile 变更 |
| colcon build | CI cache | `src/` 变更 |
| pip 依赖 | CI cache | requirements.txt 变更 |
| 模型文件 | LFS / S3 | 版本变更 |

## 并行优化

```yaml
# 并行构建多个包
build:
  parallel:
    matrix:
      - PACKAGE: [perception, planning, control, localization]
  script:
    - colcon build --packages-select ${PACKAGE}
```

## 产物管理

| 产物 | 存储 | 保留策略 |
|------|------|---------|
| 编译产物 | CI artifact | 30 天 |
| Docker 镜像 | Registry | 10 个最新版本 |
| 测试报告 | S3 / MinIO | 90 天 |
| 日志 | ELK / Loki | 30 天 |

## 故障排查

| 故障 | 诊断 | 修复 |
|------|------|------|
| 构建超时 | 依赖下载慢 | 换源 / 缓存 |
| 测试随机失败 | 竞态条件 | 固定随机种子 |
| 内存不足 | 并行度过高 | 减少并发 |
| GPU 不可用 | runner 配置 | 使用 GPU runner |
