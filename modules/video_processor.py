# video_processor.py

import cv2
import torch
import numpy as np
from pathlib import Path
import logging

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
        try:
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
            logging.info(f"输出文件将保存至: {self.output_dir}")
        except Exception as e:
            logging.error(f"初始化视频写入器失败: {e}", exc_info=True)
            raise IOError(f"无法在 '{self.output_dir}' 创建视频文件。请检查路径和写入权限。")

    def _get_combined_mask(self, predictions, frame_shape):
        """
        从模型预测中筛选出我们关心的类别，并将它们的掩码合并成一个。
        这是修复后的核心功能。
        """
        # 1. 根据图像尺寸创建一个空白的布尔掩码，确保程序健壮性
        combined_mask = np.zeros((frame_shape[0], frame_shape[1]), dtype=bool)
        
        instances = predictions["instances"]
        # 2. 如果模型没有检测到任何物体，直接返回空白掩码
        if len(instances) == 0:
            return combined_mask.astype(np.uint8) * 255
            
        # 3. 遍历所有检测到的物体
        for i in range(len(instances)):
            pred_class = instances.pred_classes[i].item()
            # 4. 如果物体类别在我们关心的类别列表中，则将其掩码合并
            if pred_class in config.CLASSES_TO_MASK:
                mask = instances.pred_masks[i].cpu().numpy()
                combined_mask = np.logical_or(combined_mask, mask)
        
        return combined_mask.astype(np.uint8) * 255


    def process_video(self):
        """
        执行单个视频的完整处理流程。
        """
        cap = cv2.VideoCapture(str(self.input_path))
        if not cap.isOpened():
            # 如果文件无法打开，则向上抛出IOError，由main.py捕获
            raise IOError(f"无法打开视频文件 {self.input_path}。文件可能已损坏或格式不支持。")
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._setup_video_writers(cap)

        frame_num = 0
        logged_progress = set() # 用于避免重复记录相同的进度百分比

        while cap.isOpened():
            try:
                ret, frame = cap.read()
                if not ret:
                    break # 视频读取完毕
                
                frame_num += 1

                # 报告关键进度节点 (25%, 50%, 75%, 100%)，避免刷屏
                progress_percent = int((frame_num / total_frames) * 100)
                milestones = [25, 50, 75, 100]
                for m in milestones:
                    if progress_percent >= m and m not in logged_progress:
                        logging.info(f"处理进度: {frame_num}/{total_frames} ({m}%)")
                        logged_progress.add(m)

                # 1. AI 推理
                predictions = self.model.predict(frame)

                # 2. 生成合并后的掩码 (传入 frame.shape 修复了核心 Bug)
                combined_mask = self._get_combined_mask(predictions, frame.shape)
                
                # 3. 生成三种输出帧
                v = Visualizer(frame[:, :, ::-1], self.metadata, scale=1.0)
                vis_output = v.draw_instance_predictions(predictions["instances"].to("cpu"))
                vis_frame = vis_output.get_image()[:, :, ::-1]

                mask_frame = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)

                inverted_mask = cv2.bitwise_not(combined_mask)
                masked_frame = cv2.bitwise_and(frame, frame, mask=inverted_mask)

                # 4. 写入视频
                self.writer_vis.write(vis_frame)
                self.writer_mask.write(mask_frame)
                self.writer_final.write(masked_frame)
            
            except Exception as e:
                # 如果处理单帧时出错，记录警告并继续处理下一帧
                logging.warning(f"处理第 {frame_num} 帧时出错，已跳过此帧。错误: {e}")
                continue

        # 释放所有资源
        logging.info("视频帧处理完成，正在保存文件...")
        cap.release()
        self.writer_vis.release()
        self.writer_mask.release()
        self.writer_final.release()