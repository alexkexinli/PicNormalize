import os
import cv2
from PIL import Image
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

def process_image(image_path, output_path):
    try:
        print("processing " + image_path)
        # 在函数内重新导入 face_recognition
        import face_recognition

        img = face_recognition.load_image_file(image_path)
        if img is None:
            print(f"无法读取图片：{image_path}")
            return

        # 使用基于 CNN 的模型进行人脸检测
        face_locations = face_recognition.face_locations(img, model='cnn')

        # 如果检测到人脸，裁剪第一张人脸区域
        if len(face_locations) > 0:
            top, right, bottom, left = face_locations[0]
            # 扩展裁剪区域，保留更多面部特征（可根据需要调整）
            h, w, _ = img.shape
            padding_w = int(0.4 * (right - left))
            padding_h = int(0.4 * (bottom - top))
            left = max(left - padding_w, 0)
            top = max(top - padding_h, 0)
            right = min(right + padding_w, w)
            bottom = min(bottom + padding_h, h)
            cropped_img = img[top:bottom, left:right]
        else:
            # 如果未检测到人脸，使用原始图片
            print(f"未检测到人脸：{image_path}")
            cropped_img = img

        # 调整图片大小，保持原始比例并填充
        target_size = (224, 224)
        h_cropped, w_cropped = cropped_img.shape[:2]
        # 计算缩放比例
        scale = min(target_size[1] / w_cropped, target_size[0] / h_cropped)
        # 计算新的尺寸
        new_w = int(w_cropped * scale)
        new_h = int(h_cropped * scale)
        resized_img = cv2.resize(cropped_img, (new_w, new_h))

        # 计算填充
        delta_w = target_size[1] - new_w
        delta_h = target_size[0] - new_h
        top_pad = delta_h // 2
        bottom_pad = delta_h - top_pad
        left_pad = delta_w // 2
        right_pad = delta_w - left_pad

        # 填充图片
        padded_img = cv2.copyMakeBorder(
            resized_img,
            top_pad, bottom_pad, left_pad, right_pad,
            cv2.BORDER_CONSTANT,
            value=[0, 0, 0]  # 黑色填充，可根据需要修改
        )

        # 保存处理后的图片
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pil_image = Image.fromarray(padded_img)
        pil_image.save(output_path)
    except Exception as e:
        print(f"处理图片 {image_path} 时出错：{e}")

def traverse_and_process(input_dir, output_dir):
    # 收集所有待处理的图片文件路径
    image_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_dir)
                destination_path = os.path.join(output_dir, relative_path, file)
                image_files.append((source_path, destination_path))

    # 使用线程池并行处理图片
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_image, src, dst) for src, dst in image_files]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"处理图片时出错：{e}")

if __name__ == "__main__":
    # 设置多进程启动方式为 'spawn'
    multiprocessing.set_start_method('spawn')

    input_directory = '/mnt/e/testPicCut/src'  # 替换为您的源文件夹路径
    output_directory = '/mnt/e/testPicCut/des'  # 替换为您的目标文件夹路径
    traverse_and_process(input_directory, output_directory)