# ComfyUI-WatermarkNode
可以快速给图片加上水印，对于批量加水印的工作效率大大增加
1.文件结构
ComfyUI/custom_nodes/
└── watermark_node/
    ├── __init__.py
    └── nodes.py
2.参数说明
image: 主图
watermark: 水印图片（透明底）
opacity: 透明度 (0-1)
tiles_per_row：每行平铺几个水印（比如填 3，就是横着铺 3 个）
overlap：重叠程度：0=刚好铺满，0.3=重叠30%，-0.3=间隔30%
invert_mask：遮罩反转(透明底变黑勾选)
<img width="1349" height="904" alt="image" src="https://github.com/user-attachments/assets/91ef5246-d675-4ce0-be77-83d7c5663f8c" />

