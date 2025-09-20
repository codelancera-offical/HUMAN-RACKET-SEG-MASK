# main.py

import argparse
import logging
from pathlib import Path

# 导入我们自己的模块
import config
from modules.video_processor import VideoProcessor
from logger_config import setup_logger

def main():
    """
    主函数，负责解析命令行参数、扫描视频文件并调度处理流程。
    """
    # 在程序最开始处初始化日志记录器
    setup_logger()

    # 1. 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="自动处理网球视频，分离运动员和球拍的运动。")
    parser.add_argument(
        "--input_folder",
        type=str,
        required=True,
        help="包含源视频文件的文件夹路径。"
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        required=True,
        help="用于保存所有处理结果的顶层文件夹路径。"
    )
    args = parser.parse_args()

    # 2. 将字符串路径转换为更强大、更易于操作的Path对象
    input_dir = Path(args.input_folder)
    output_dir = Path(args.output_folder)

    # 3. 验证路径并准备环境
    if not input_dir.is_dir():
        logging.error(f"输入文件夹不存在 -> {input_dir}")
        return

    # 创建顶层输出文件夹 (如果不存在)
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"输入文件夹: {input_dir}")
    logging.info(f"输出将保存至: {output_dir}")

    # 4. 扫描输入文件夹，查找所有支持的视频文件
    video_files = []
    for ext in config.SUPPORTED_VIDEO_EXTENSIONS:
        video_files.extend(input_dir.glob(f"*{ext}"))

    if not video_files:
        logging.error("在输入文件夹中未找到任何支持的视频文件。")
        logging.error(f"支持的格式: {config.SUPPORTED_VIDEO_EXTENSIONS}")
        return

    logging.info(f"发现 {len(video_files)} 个视频文件，准备开始处理...")

    # 5. 遍历每个视频文件，启动处理流程
    successful_count = 0
    failed_count = 0
    for i, video_path in enumerate(video_files):
        try:
            logging.info("="*50)
            logging.info(f"==> 开始处理第 {i+1}/{len(video_files)} 个视频: {video_path.name}")

            # 为当前视频创建专属的输出子文件夹
            video_output_subdir = output_dir / video_path.stem
            video_output_subdir.mkdir(exist_ok=True)

            # 实例化视频处理器，并传入具体的任务路径
            processor = VideoProcessor(
                input_path=video_path,
                output_dir=video_output_subdir
            )

            # 启动处理！
            processor.process_video()
            logging.info(f"✅ {video_path.name} 处理完成。")
            successful_count += 1

        except Exception as e:
            # 捕获处理单个视频时发生的所有异常
            logging.error(f"处理视频 {video_path.name} 时发生严重错误，已跳过。")
            # exc_info=True 会将详细的错误堆栈信息记录到日志中，便于调试
            logging.error(f"错误详情: {e}", exc_info=True)
            failed_count += 1

    logging.info("="*50)
    logging.info("🎉 所有视频处理任务已全部完成！")
    logging.info(f"总计: {len(video_files)} 个, 成功: {successful_count} 个, 失败: {failed_count} 个。")


if __name__ == "__main__":
    main()