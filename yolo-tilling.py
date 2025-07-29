import os
import cv2
from PIL import Image

# Config
IMG_DIR = r'C:\Users\...\images'           # directory with input .jpg images
LABEL_DIR = r'C:\Users\...\text-files'         # directory with matching YOLO .txt files
OUTPUT_IMG_DIR = r'C:\Users\...output-images'
OUTPUT_LABEL_DIR = r'C:\Users\...\output-labels'

CROP_SIZE = 640 #can be changed!
OVERLAP = 0.5  # 0.5 = 50% overlap
MIN_VISIBILITY = 0.9  # Only include bboxes where at least 90% is visible 

def make_dirs():
    os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_LABEL_DIR, exist_ok=True)

def parse_yolo_annotation(txt_path, img_width, img_height):
    boxes = []
    with open(txt_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            cls, x_center, y_center, width, height = map(float, parts)
            xc = x_center * img_width
            yc = y_center * img_height
            w = width * img_width
            h = height * img_height
            xmin = int(xc - w / 2)
            xmax = int(xc + w / 2)
            ymin = int(yc - h / 2)
            ymax = int(yc + h / 2)
            boxes.append((int(cls), xmin, ymin, xmax, ymax))
    return boxes

def save_crop_and_label(crop_img, crop_boxes, crop_index, base_filename, crop_coords):
    crop_filename = f"{base_filename}_crop{crop_index}.jpg"
    crop_path = os.path.join(OUTPUT_IMG_DIR, crop_filename)
    Image.fromarray(crop_img).save(crop_path)

    crop_txt_path = os.path.join(OUTPUT_LABEL_DIR, crop_filename.replace('.jpg', '.txt'))
    img_h, img_w = crop_img.shape[:2]

    with open(crop_txt_path, 'w') as f:
        for cls, xmin, ymin, xmax, ymax in crop_boxes:
            x_c = ((xmin + xmax) / 2 - crop_coords[0]) / img_w
            y_c = ((ymin + ymax) / 2 - crop_coords[1]) / img_h
            w = (xmax - xmin) / img_w
            h = (ymax - ymin) / img_h
            f.write(f"{cls} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")

def crop_image(img_path, label_path, base_filename):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    step = int(CROP_SIZE * (1 - OVERLAP))

    if not os.path.exists(label_path) or os.path.getsize(label_path) == 0:
        return

    boxes = parse_yolo_annotation(label_path, w, h)
    crop_index = 0

    for y in range(0, h - CROP_SIZE + 1, step):
        for x in range(0, w - CROP_SIZE + 1, step):
            crop = img[y:y+CROP_SIZE, x:x+CROP_SIZE]
            crop_boxes = []

            for cls, xmin, ymin, xmax, ymax in boxes:
                inter_xmin = max(xmin, x)
                inter_ymin = max(ymin, y)
                inter_xmax = min(xmax, x + CROP_SIZE)
                inter_ymax = min(ymax, y + CROP_SIZE)

                inter_area = max(0, inter_xmax - inter_xmin) * max(0, inter_ymax - inter_ymin)
                orig_area = (xmax - xmin) * (ymax - ymin)

                if inter_area / orig_area >= MIN_VISIBILITY:
                    crop_boxes.append((cls, inter_xmin, inter_ymin, inter_xmax, inter_ymax))

            if crop_boxes:
                save_crop_and_label(crop, crop_boxes, crop_index, base_filename, (x, y))
                crop_index += 1

if __name__ == "__main__":
    make_dirs()
    image_files = [f for f in os.listdir(IMG_DIR) if f.lower().endswith('.jpg')]

    for img_file in image_files:
        base_filename = os.path.splitext(img_file)[0]
        img_path = os.path.join(IMG_DIR, img_file)
        txt_path = os.path.join(LABEL_DIR, base_filename + '.txt')

        if not os.path.exists(txt_path):
            print(f"Warning: Missing label for {img_file}")
            continue

        crop_image(img_path, txt_path, base_filename)

    print("✅ Cropping complete. Check:", OUTPUT_IMG_DIR)
