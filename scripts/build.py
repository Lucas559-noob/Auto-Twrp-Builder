from twrpdtgen.device_tree import DeviceTree
import argparse
import os
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
    
    if os.getenv('GITHUB_OUTPUT', ''):
        with open(os.getenv('GITHUB_OUTPUT', ''), 'w') as f:
            f.write(f'DEVICE_NAME={device_tree.device_info.manufacturer}\n')
            f.write(f'MAKEFILE_NAME=omni_{device_tree.device_info.codename}\n')
            f.write(f'DEVICE_PATH={device_path}\n')
    
    device_tree.dump_to_folder(Path(args.output))
    
    # Create omni.dependencies file if it doesn't exist
    deps_file = os.path.join(device_path, 'omni.dependencies')
    if not os.path.exists(deps_file):
        print(f"[INFO] Creating minimal dependencies file at {deps_file}")
        os.makedirs(os.path.dirname(deps_file), exist_ok=True)
        with open(deps_file, 'w') as f:
            f.write('[]\n')
        print(f"[INFO] Dependencies file created successfully")
    else:
        print(f"[INFO] Dependencies file already exists at {deps_file}")
    
    with open(device_path + os.sep + 'Android.bp', 'r') as f:
        print(f.read())
