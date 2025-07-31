Image Tiling Script for Object Detection (YOLO Format)
Training object detection models like YOLO on high-resolution imagery often leads to annotation issues, especially when small objects (e.g., weeds) are downscaled or lost.
This script addresses the issue by tiling large images into smaller crops while preserving object scale and corresponding label data.

Key Features
-Tiling of high-res images into overlapping/non-overlapping tiles
-Automatic label adjustment for each tile (YOLO format)
-Supports .jpg/.png images and .txt YOLO annotations

Input
--The folder of high-resolution imagery (example - mine were arround 2k x 2k , 3k x 3k and 4k x 4k)
--Corresponding YOLO-format predictions (.txt annotation files)

Output
-Folder of cropped images
-Folder of annotations 

Acknowledgements
Based on ideas from (https://github.com/Jordan-Pierce/yolo-tiling), adapted and modified for agricultural weed datasets, structure assisted by ChatGPT.

License
-For research purposes only-
