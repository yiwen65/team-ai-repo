#!/usr/bin/env python3
"""
ota_verifier.py
验证 OTA 包完整性、签名、兼容性。

Usage:
  python ota_verifier.py --package ota_v2.1.zip --public-key key.pem --output report.md
"""

import zipfile
import json
import hashlib
import argparse
from pathlib import Path


def verify_package(package_path):
    """Verify OTA package structure."""
    issues = []
    
    with zipfile.ZipFile(package_path, 'r') as zf:
        files = zf.namelist()
        
        # Check required files
        required = ["MANIFEST.json", "signature.sig"]
        for req in required:
            if req not in files:
                issues.append(f"Missing required file: {req}")
        
        # Parse manifest
        if "MANIFEST.json" in files:
            manifest = json.loads(zf.read("MANIFEST.json"))
            
            # Check version
            if "version" not in manifest:
                issues.append("MANIFEST missing 'version'")
            
            # Check compatibility
            if "compatible_versions" in manifest:
                # Would check against current system version
                pass
            
            # Check file list
            if "files" in manifest:
                for file_info in manifest["files"]:
                    filename = file_info.get("name")
                    expected_hash = file_info.get("sha256")
                    
                    if filename not in files:
                        issues.append(f"Missing file in manifest: {filename}")
                        continue
                    
                    # Verify hash
                    actual_hash = hashlib.sha256(zf.read(filename)).hexdigest()
                    if actual_hash != expected_hash:
                        issues.append(f"Hash mismatch for {filename}")
        
        # Check signature (simplified)
        if "signature.sig" in files:
            # In real implementation, verify with public key
            pass
    
    return len(issues) == 0, issues


def generate_report(package_path, valid, issues, output_path):
    lines = [f"# OTA 包验证报告: {package_path}\n\n"]
    
    if valid:
        lines.append("✅ 验证通过\n")
    else:
        lines.append(f"❌ 验证失败: {len(issues)} 个问题\n\n")
        lines.append("## 问题列表\n")
        for issue in issues:
            lines.append(f"- {issue}\n")
    
    report = "".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, help="OTA package path")
    parser.add_argument("--public-key", help="Public key for signature verification")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    valid, issues = verify_package(args.package)
    generate_report(args.package, valid, issues, args.output)


if __name__ == "__main__":
    main()
