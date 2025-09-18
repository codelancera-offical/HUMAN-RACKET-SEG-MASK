import cv2
import torch
import numpy as np
from pathlib import Path
import sys

# Detectron2 相关库
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

# 导入我们自己的模块
import config
from .segmentation_model import SegmentationModel

class VideoProcessor:
    """
    负责处理单个视频文件，并生成所有三种输出视频的核心类。
    """
    def __init__(self, input_path: Path, output_dir: Path):
        """
        构造函数
        参数:
            input_path: (pathlib.Path) 单个输入视频的完整路径。
            output_dir: (pathlib.Path) 所有输出视频应保存到的文件夹路径。
        """
        self.input_path = input_path
        self.output_dir = output_dir
        self.model = SegmentationModel()

        # 为可视化准备Detectron2的元数据 (用于获取类别名称等)
        self.metadata = MetadataCatalog.get(config.MODEL_CONFIG_FILE.replace(".yaml", ""))

    def _setup_video_writers(self, cap):
        """
        根据输入视频的属性，初始化所有三个视频写入器。
        """
        # 获取视频的帧率(fps)和尺寸(width, height)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 定义视频编码器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # 构建三个输出文件的完整路径
        vis_path = self.output_dir / f"{self.input_path.stem}{config.OUTPUT_FILENAMES['visualization']}"
        mask_path = self.output_dir / f"{self.input_path.stem}{config.OUTPUT_FILENAMES['mask_only']}"
        final_path = self.output_dir / f"{self.input_path.stem}{config.OUTPUT_FILENAMES['masked_final']}"

        # 创建三个写入器实例
        self.writer_vis = cv2.VideoWriter(str(vis_path), fourcc, fps, (width, height))
        self.writer_mask = cv2.VideoWriter(str(mask_path), fourcc, fps, (width, height))
        self.writer_final = cv2.VideoWriter(str(final_path), fourcc, fps, (width, height))
        print(f"    - 输出文件将保存至: {self.output_dir}")

    def _get_combined_mask(self, predictions):
        """
        从模型预测中筛选出我们关心的类别，并将它们的掩码合并成一个。
        """
        instances = predictions["instances"]
        # 创建一个与图像等大的全黑(False)布尔掩码
        combined_mask = np.zeros_like(instances.pred_masks[0].cpu().numpy(), dtype=bool)

        for i in range(len(instances)):
            pred_class = instances.pred_classes[i].item()
            score = instances.scores[i].item()

            if pred_class in config.CLASSES_TO_MASK and score >= config.CONFIDENCE_THRESHOLD:
                mask = instances.pred_masks[i].cpu().numpy()
                combined_mask = np.logical_or(combined_mask, mask)
        
        return combined_mask.astype(np.uint8) * 255


    def process_video(self):
        """
        执行单个视频的完整处理流程。
        """
        cap = cv2.VideoCapture(str(self.input_path))
        if not cap.isOpened():
            print(f"错误：无法打开视频文件 {self.input_path}")
            return
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._setup_video_writers(cap)

        frame_num = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_num += 1
            # 打印进度
            sys.stdout.write(f"\r    - 正在处理帧: {frame_num}/{total_frames}")
            sys.stdout.flush()

            # 1. AI 推理
            predictions = self.model.predict(frame)

            # 2. 生成合并后的掩码
            combined_mask = self._get_combined_mask(predictions)
            
            # 3. 生成三种输出帧
            # 可视化帧
            v = Visualizer(frame[:, :, ::-1], self.metadata, scale=1.0)
            vis_output = v.draw_instance_predictions(predictions["instances"].to("cpu"))
            vis_frame = vis_output.get_image()[:, :, ::-1]

            # 纯掩码帧
            mask_frame = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)

            # 最终遮蔽帧
            inverted_mask = cv2.bitwise_not(combined_mask)
            masked_frame = cv2.bitwise_and(frame, frame, mask=inverted_mask)

            # 4. 写入视频
            self.writer_vis.write(vis_frame)
            self.writer_mask.write(mask_frame)
            self.writer_final.write(masked_frame)

        # 释放所有资源
        print("\n    - 视频帧处理完成，正在保存文件...")
        cap.release()
        self.writer_vis.release()
        self.writer_mask.release()
        self.writer_final.release()