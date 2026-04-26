import os
import shutil

# Correct paths based on kagglehub output
ds1_path = r"C:\Users\Lenovo\.cache\kagglehub\datasets\thammuio\all-agriculture-related-datasets-for-india\versions\4"
ds2_path = r"C:\Users\Lenovo\.cache\kagglehub\datasets\akshatgupta7\crop-yield-in-indian-states-dataset\versions\1"
target_dir = r"D:\Farm-IQ - Copy\Data-raw"

if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"Created directory: {target_dir}")

def move_files(src, dst):
    for root, dirs, files in os.walk(src):
        for file in files:
            if file.endswith('.csv'):
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst, file)
                # Avoid overwriting with same name if they are different datasets
                if os.path.exists(dst_file):
                    name, ext = os.path.splitext(file)
                    dst_file = os.path.join(dst, f"{name}_{os.path.basename(src)}{ext}")
                
                shutil.copy2(src_file, dst_file)
                print(f"Copied {file} to {dst_file}")

print("Moving files from Dataset 1...")
move_files(ds1_path, target_dir)

print("\nMoving files from Dataset 2...")
move_files(ds2_path, target_dir)

print("\nFinal contents of Data-raw:")
print(os.listdir(target_dir))
