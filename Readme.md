# 网球视频干扰消除工具 (Tennis Video Interference Eliminator)

[![Python](https://img-shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/Framework-Detectron2-orange.svg)](https://github.com/facebookresearch/detectron2)
[![Code Style](https://img.shields.io/badge/Code%20Style-Clean-brightgreen.svg)]()

一个基于Detectron2深度学习框架的自动化批处理工具，用于识别网球视频中的运动员和球拍，并生成三种不同的可视化分析视频。

---

## 核心功能

-   **命令行驱动**: 通过简单的命令即可指定输入和输出文件夹。
-   **自动批处理**: 自动扫描并处理指定文件夹内的所有视频文件。
-   **结构化输出**: 为每个输入视频创建一个独立的子文件夹来存放结果，保持文件整洁。
-   **多种产出**: 对每个视频生成三种分析结果，满足不同需求：
    1.  **过程可视化视频**: 用于直观评估模型性能。
    2.  **纯净掩码视频**: 作为数据产物，用于后续量化分析。
    3.  **最终遮蔽视频**: 消除干扰后的最终成果。
-   **高精度模型**: 基于Detectron2的预训练模型，确保分割的准确性。

---

## 输出示例

对于每一个输入视频（如 `game1.mp4`），工具将在输出文件夹内创建一个名为 `game1` 的子文件夹，并生成以下三个视频文件：

#### 1. `game1_visualization.mp4`
> **过程可视化视频**：在原始视频画面上，被识别出的运动员和球拍会被半透明的彩色蒙版实时覆盖。这可以非常直观地看出模型的识别效果。

#### 2. `game1_mask_only.mp4`
> **纯净掩码视频**：纯黑白视频。背景为黑色，所有被识别出的运动员和球拍区域显示为白色轮廓。这个视频清晰地展示了干扰物在时空中的运动轨迹。

#### 3. `game1_masked_final.mp4`
> **最终遮蔽视频**：在原始视频画面中，将所有被识别出的运动员和球拍区域完全涂黑。这个视频消除了主要的视觉干扰，是进行后续网球轨迹分析的理想输入。

---

## 项目结构