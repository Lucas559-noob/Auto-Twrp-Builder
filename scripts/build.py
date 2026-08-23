from twrpdtgen.device_tree import DeviceTree
import argparse
import os
import json
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Auto-Twrp-Builder")
    parser.add_argument('-i', '--input', type=str, default='', help='Recovery/Boot Image')
    parser.add_argument('-o', '--output', type=str, default='', help='Output path')
    args = parser.parse_args()
    if not args.input or not args.output:
        parser.print_help()
        exit()
    if not os.path.exists(args.output):
        os.makedirs(args.output, exist_ok=True)
    
    device_tree = DeviceTree(Path(args.input))
    device_path = os.path.basename(args.output) + os.sep + device_tree.device_info.manufacturer + os.sep + device_tree.device_info.codename
    
    print(f"[INFO] Device detected: {device_tree.device_info.codename}")
    print(f"[INFO] Manufacturer: {device_tree.device_info.manufacturer}")
    
    if os.getenv('GITHUB_OUTPUT', ''):
        with open(os.getenv('GITHUB_OUTPUT', ''), 'w') as f:
            f.write(f'DEVICE_NAME={device_tree.device_info.manufacturer}\n')
            f.write(f'MAKEFILE_NAME=omni_{device_tree.device_info.codename}\n')
            f.write(f'DEVICE_PATH={device_path}\n')
    
    device_tree.dump_to_folder(Path(args.output))
    
    # Verify Android.bp was created and contains content
    android_bp_path = os.path.join(device_path, 'Android.bp')
    if not os.path.exists(android_bp_path):
        print(f"[ERROR] Android.bp not created at {android_bp_path}")
        exit(1)

    with open(android_bp_path, 'r') as f:
        content = f.read()
        if not content.strip():
            print(f"[ERROR] Android.bp is empty")
            exit(1)
        print(f"[INFO] Android.bp generated successfully with {len(content)} bytes")
    
    # Create omni.dependencies file with proper HAL dependencies
    deps_file = os.path.join(device_path, 'omni.dependencies')
    if not os.path.exists(deps_file):
        print(f"[INFO] Creating dependencies file at {deps_file}")
        os.makedirs(os.path.dirname(deps_file), exist_ok=True)
        
        # Check if vendor/omni already exists in the manifest
        manifest_path = os.path.join(os.getcwd(), '.repo/manifest.xml')
        skip_vendor_omni = False
        
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as mf:
                    manifest_content = mf.read()
                    if 'vendor/omni' in manifest_content:
                        skip_vendor_omni = True
                        print("[INFO] vendor/omni already in manifest, skipping to avoid duplicates")
            except Exception as e:
                print(f"[WARNING] Could not read manifest: {e}")
        
        # Build dependencies list
        deps = []
        
        if not skip_vendor_omni:
            deps.append({
                "repository": "vendor/omni",
                "target_path": "vendor/omni",
                "branch": "twrp-8.1"
            })
        
        # Always add hardware/qcom as it was missing
        deps.append({
            "repository": "hardware/qcom",
            "target_path": "hardware/qcom",
            "branch": "twrp-8.1"
        })
        
        with open(deps_file, 'w') as f:
            f.write(json.dumps(deps, indent=2) + '\n')
        
        print(f"[INFO] Dependencies file created successfully")
    else:
        print(f"[INFO] Dependencies file already exists at {deps_file}")
    
    with open(android_bp_path, 'r') as f:
        print(f.read())
