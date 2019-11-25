import argparse
import glob
from pathlib import Path
import os

import cv2
import dlib

# 参考: https://qiita.com/ligerbolt/items/2bfb28b5cd1eaf0fa816


class FaceTrimmer:
    def __init__(self, resize_height=None, resize_width=None, save_dir=None):
        self.resize_height = resize_height if resize_height is not None else 64
        self.resize_width = resize_width if resize_width is not None else 64
        self.save_dir = save_dir if save_dir is not None else \
            './images/trimmed/'

    def trimming_face(self, image_dir_path_list):
        detector = dlib.get_frontal_face_detector()

        for image_dir_path in image_dir_path_list:
            target_dir_name = Path(image_dir_path).name

            img_count = 1
            for image_path in glob.glob(str(Path().cwd().joinpath(image_dir_path).joinpath('*.jpg'))):
                img = cv2.imread(image_path, cv2.IMREAD_COLOR)
                # 読み込めない画像はスキップ
                if img is None or len(img) == 0:
                    print('-- can\'t load image...')
                    continue

                cv_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                faces = detector(cv_img, 1)

                for face in faces:
                    height, width = img.shape[:2]

                    top = face.top()
                    bottom = face.bottom()
                    left = face.left()
                    right = face.right()

                    if not top < 0 and left < 0 and bottom > height and right > width:
                        continue
                    else:
                        dst_img = img[top:bottom, left:right]

                        # 読み込めない画像はスキップ
                        if dst_img.size == 0:
                            print('-- can\'t load image...')
                            img_count += 1
                            continue

                        face_img = cv2.resize(dst_img, (self.resize_height, self.resize_width))
                        save_dir = Path(self.save_dir).parent.joinpath('trimmed').joinpath(target_dir_name)
                        os.makedirs(save_dir, exist_ok=True)
                        new_img_name = str(save_dir.joinpath(str(img_count) + '.jpg'))
                        print(new_img_name)
                        cv2.imwrite(new_img_name, face_img)
                        img_count += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target_dir', nargs="*", required=True)
    parser.add_argument('--height')
    parser.add_argument('--width')
    args = parser.parse_args()

    ft = FaceTrimmer(resize_height=args.height, resize_width=args.width)
    ft.trimming_face(args.target_dir)
