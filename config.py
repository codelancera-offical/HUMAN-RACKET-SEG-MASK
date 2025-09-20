import torch

# --- 1. 模型与推理配置 ---
# Detectron2 模型配置文件名
MODEL_CONFIG_FILE = "COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"

# 模型置信度阈值 (0.0 到 1.0)
# 只有当模型对物体的识别置信度高于此值时，才会被采纳
CONFIDENCE_THRESHOLD = 0.7

# 需要识别并处理的物体类别ID (基于 COCO 数据集)
# 'person' 的类别ID是 0, 'sports racket' 的类别ID是 38
CLASSES_TO_MASK = [0, 38] 

# --- 2. 输出文件名模板 ---
# 定义三种输出视频的文件名后缀
# 主程序会自动将 "输入视频名" + "这里的后缀" 组合成最终文件名
OUTPUT_FILENAMES = {
    "visualization": "_visualization.mp4",
    "mask_only": "_mask_only.mp4",
    "masked_final": "_masked_final.mp4"
}

# --- 3. 批处理与环境配置 ---
# main.py 在扫描输入文件夹时，会查找这些扩展名的文件
SUPPORTED_VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]

# 自动检测是否有可用的 CUDA (NVIDIA GPU) 设备
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- 4. 可视化效果配置 ---
# 在“过程可视化视频”中，覆盖在目标上的蒙版的透明度 (0.0 - 1.0)
VISUALIZATION_ALPHA = 0.5