#!/usr/bin/env python3
"""
calib_validator.py
对标定结果执行完整验证 checklist。

Usage:
  python calib_validator.py --calib calib.yaml --vehicle-config vehicle.yaml --output validation.md
"""

import yaml
import argparse
from datetime import datetime


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def validate_calib(calib, vehicle):
    """Run validation checks."""
    checks = []
    
    # 1. Version check
    version = calib.get("calib_version", 0)
    checks.append(("标定版本", version >= 2, f"版本: {version}"))
    
    # 2. Required fields
    required = ["vehicle_model", "sensor_config", "calib_date", "cameras", "extrinsics"]
    for field in required:
        exists = field in calib
        checks.append((f"必需字段: {field}", exists, f"{'存在' if exists else '缺失'}"))
    
    # 3. Camera count matches vehicle config
    expected_cams = vehicle.get("num_cameras", 0)
    actual_cams = len(calib.get("cameras", {}))
    checks.append((
        "相机数量一致",
        expected_cams == actual_cams,
        f"期望: {expected_cams}, 实际: {actual_cams}"
    ))
    
    # 4. Each camera has required params
    for cam_name, cam_config in calib.get("cameras", {}).items():
        has_K = "K" in cam_config
        has_D = "D" in cam_config
        has_size = "image_size" in cam_config
        checks.append((
            f"相机 {cam_name} 内参完整",
            has_K and has_D and has_size,
            f"K: {has_K}, D: {has_D}, size: {has_size}"
        ))
        
        # Check distortion model
        model = cam_config.get("distortion_model", "")
        valid_model = model in ["pinhole", "kannala-brandt", "mei", "scaramuzza"]
        checks.append((
            f"相机 {cam_name} 畸变模型",
            valid_model,
            f"模型: {model}"
        ))
    
    # 5. Extrinsics completeness
    extrinsics = calib.get("extrinsics", {})
    expected_pairs = vehicle.get("extrinsic_pairs", [])
    for pair in expected_pairs:
        exists = pair in extrinsics
        checks.append((
            f"外参: {pair}",
            exists,
            f"{'存在' if exists else '缺失'}"
        ))
    
    # 6. Validation result
    has_validation = "validation_result" in calib
    checks.append((
        "标定验证结果",
        has_validation and calib.get("validation_result") == "PASS",
        f"结果: {calib.get('validation_result', '未记录')}"
    ))
    
    # 7. Temperature record
    has_temp = "temperature" in calib
    checks.append((
        "标定温度记录",
        has_temp,
        f"温度: {calib.get('temperature', '未记录')}°C"
    ))
    
    # 8. Hash/checksum
    has_hash = "hash" in calib
    checks.append((
        "标定文件校验",
        has_hash,
        f"{'存在' if has_hash else '缺失'}"
    ))
    
    return checks


def generate_report(checks, output_path):
    lines = [f"# 标定验证报告\n"]
    lines.append(f"生成时间: {datetime.now().isoformat()}\n\n")
    lines.append("| 检查项 | 结果 | 说明 |")
    lines.append("|--------|------|------|")
    
    passed = 0
    failed = 0
    
    for name, ok, detail in checks:
        status = "✅ 通过" if ok else "❌ 失败"
        if not ok:
            failed += 1
        else:
            passed += 1
        lines.append(f"| {name} | {status} | {detail} |")
    
    lines.append(f"\n## 汇总\n")
    lines.append(f"- 通过: {passed}/{len(checks)}\n")
    lines.append(f"- 失败: {failed}/{len(checks)}\n")
    
    if failed == 0:
        lines.append("\n✅ 所有检查通过，标定文件可入库\n")
    elif failed <= 2:
        lines.append("\n⚠️ 少量问题，建议修复后入库\n")
    else:
        lines.append("\n❌ 严重问题较多，标定文件不可使用\n")
    
    report = "\n".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calib", required=True, help="Calibration YAML")
    parser.add_argument("--vehicle-config", required=True, help="Vehicle config YAML")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    calib = load_yaml(args.calib)
    vehicle = load_yaml(args.vehicle_config)
    
    checks = validate_calib(calib, vehicle)
    generate_report(checks, args.output)


if __name__ == "__main__":
    main()
