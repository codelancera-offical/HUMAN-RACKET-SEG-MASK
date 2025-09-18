import torch
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo

# 导入我们自己的配置文件
import config

class SegmentationModel:
    """
    一个封装了Detectron2模型的包装类。
    它的职责是：
    1. 在初始化时，根据config文件加载和配置好一个预训练的分割模型。
    2. 提供一个简单的 `predict` 方法，接收图像并返回原始的预测结果。
    """
    def __init__(self):
        """
        构造函数，负责初始化模型。
        """
        # 1. 创建一个Detectron2的标准配置对象
        cfg = get_cfg()

        # 2. 从Detectron2的模型库(model zoo)中加载我们指定的模型配置文件
        # 这会告诉Detectron2我们要使用什么样的模型架构
        cfg.merge_from_file(model_zoo.get_config_file(config.MODEL_CONFIG_FILE))

        # 3. 指定具体的、预训练好的模型权重文件
        # 这会加载已经训练好的“大脑”
        cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(config.MODEL_CONFIG_FILE)

        # 4. 设置推理设备 (使用GPU还是CPU)
        cfg.MODEL.DEVICE = config.DEVICE

        # 5. 设定置信度阈值
        # 只有得分高于这个值的实例才会被认为是有效的检测结果
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = config.CONFIDENCE_THRESHOLD

        # 6. 基于最终的配置，创建一个“默认预测器”实例
        # 这个预测器对象就是我们用来进行实际图像分析的工具
        self.predictor = DefaultPredictor(cfg)
        print("✅ 分割模型加载成功，已准备就绪。")


    def predict(self, image_bgr: 'np.ndarray') -> dict:
        """
        对单张BGR格式的图像进行实例分割。

        参数:
            image_bgr: 一个NumPy数组，代表BGR格式的图像。

        返回:
            一个字典，包含了Detectron2模型输出的原始预测信息。
        """
        # 直接调用预测器并返回结果
        # 复杂的AI计算在这里发生
        return self.predictor(image_bgr)