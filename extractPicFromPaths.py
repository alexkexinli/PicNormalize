import os
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_image_file(filename):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    ext = os.path.splitext(filename)[1].lower()
    return ext in image_extensions

def generate_unique_filename(filepath, existing_files_lock, existing_files):
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    counter = 1
    with existing_files_lock:
        original_filename = filename
        while filename in existing_files:
            filename = f"{name}_{counter}{ext}"
            counter += 1
        existing_files.add(filename)
    return os.path.join(directory, filename)

def copy_image_file(source_file, target_directory, existing_files_lock, existing_files):
    filename = os.path.basename(source_file)
    dest_path = os.path.join(target_directory, filename)
    dest_path = generate_unique_filename(dest_path, existing_files_lock, existing_files)
    try:
        shutil.copy2(source_file, dest_path)
        print(f"已复制文件: {source_file} -> {dest_path}")
    except Exception as e:
        print(f"复制文件时出错: {source_file}，错误信息: {e}")

def collect_image_files(paths):
    image_files = []
    for path in paths:
        if os.path.isfile(path):
            if is_image_file(path):
                image_files.append(path)
                print(f"找到图片文件: {path}")
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if is_image_file(file):
                        source_file = os.path.join(root, file)
                        image_files.append(source_file)
                        print(f"找到图片文件: {source_file}")
        else:
            print(f"路径 '{path}' 既不是文件也不是文件夹。")
    return image_files

def copy_images_multithreaded(paths, target_directory, max_workers=20):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        print(f"已创建目标文件夹: {target_directory}")

    existing_files_lock = threading.Lock()
    existing_files = set(os.listdir(target_directory))

    image_files = collect_image_files(paths)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for image_file in image_files:
            futures.append(executor.submit(copy_image_file, image_file, target_directory, existing_files_lock, existing_files))

        for future in as_completed(futures):
            # 可以在这里处理每个线程的结果，如果需要的话
            pass

if __name__ == "__main__":
    # 示例用法:
    # python script.py target_directory path1 path2 path3 ...

    # if len(sys.argv) < 3:
    #     print("用法: python script.py target_directory path1 [path2 ...]")
    #     sys.exit(1)

    target_directory = "/mnt/e/PeopleFaceToTrain/celeb-df-v1/0_real"
    paths = ["/mnt/e/testPicCut/des/celeb-df-v1/Celeb-real","/mnt/e/testPicCut/des/celeb-df-v1/YouTube-real"]
    copy_images_multithreaded(paths, target_directory)

    target_directory = "/mnt/e/PeopleFaceToTrain/celeb-df-v1/1_fake"
    paths = ["/mnt/e/testPicCut/des/celeb-df-v1/Celeb-synthesis"]
    copy_images_multithreaded(paths, target_directory)

    target_directory = "/mnt/e/PeopleFaceToTrain/celeb-df-v2/0_real"
    paths = ["/mnt/e/testPicCut/des/Celeb-DF-v2/Celeb-real","/mnt/e/testPicCut/des/Celeb-DF-v2/YouTube-real"]
    copy_images_multithreaded(paths, target_directory)

    target_directory = "/mnt/e/PeopleFaceToTrain/celeb-df-v2/1_fake"
    paths = ["/mnt/e/testPicCut/des/celeb-df-v1/Celeb-synthesis"]
    copy_images_multithreaded(paths, target_directory)
