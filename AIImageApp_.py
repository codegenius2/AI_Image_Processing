import sys

import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout, QCheckBox,
    QPushButton, QSlider, QFileDialog, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame
)
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QMimeData
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from image_processing import ImageProcessing

class ImageApp(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.create_buttons_layout()
        self.create_image_display()
        self.create_sliders()
        self.setLayout(self.main_layout)
        self.setWindowTitle("Photo Correction App")
        self.image_paths = []
        self.thumbnails = []
        self.setAcceptDrops(True)

    def create_buttons_layout(self):
        correction_buttons_layout = QHBoxLayout()
        overview_frame = QWidget()
        overview_frame.setStyleSheet("background-color: #9bf28a; padding: 10px;")
        overview_buttons_layout = QVBoxLayout(overview_frame)
        options = ["補正系", "トリミング系", "選定系"]
        for option in options:
            button = QPushButton(option)
            button.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
            overview_buttons_layout.addWidget(button)
        correction_buttons_layout.addWidget(overview_frame)
        main_button_layout = QVBoxLayout()
        options = [
            "①全体の露出補正", "②手前と奥の露出統一", "③色補正",
            "④水平補正(人物を切らない)", "⑤水平補正(人物を切る)", "⑥トリミング",
            "⑦ブレ、ピンボケ", "⑧目瞑り", "⑨顔の重なり", "⑩類似写真"
        ]

        for index, option in enumerate(options, 1):
            button = QPushButton(option)
            button.setStyleSheet(f"font-size: 16px; background-color: #ADD8E6; margin: 5px;")
            button.clicked.connect(lambda _, i=index: self.handle_correction(i))
            main_button_layout.addWidget(button)

        correction_buttons_layout.addLayout(main_button_layout)
        self.main_layout.addLayout(correction_buttons_layout)

    def create_image_display(self):
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

    def create_sliders(self):
        self.brightness_slider = self.create_slider("明るさを調整する")
        self.color_slider = self.create_slider("色を調整する")
        self.contrast_slider = self.create_slider("コントラストを調整する")

    def create_slider(self, label_text):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 200)
        slider.setValue(100)
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 15px;")
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(slider)
        return slider

    def add_images(self, files):
        for file in files:
            if os.path.isfile(file):
                self.image_paths.append(file)
                self.display_thumbnail(file)

    def display_thumbnail(self, image_path):
        row = len(self.image_paths) // 4
        col = len(self.image_paths) % 4
        pixmap = QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio)

        frame = QFrame()
        frame.setStyleSheet("background-color: #c1c2be; padding: 5px;")

        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_widget = QVBoxLayout()
        image_widget.addWidget(image_label)

        checkbox = QCheckBox()
        image_widget.addWidget(checkbox)

        frame.setLayout(image_widget)
        self.grid_layout.addWidget(frame, row, col)
        self.thumbnails.append((frame, image_path))

    def handle_correction(self, correction_type):
        """Handles the selected correction type."""
        print(f"Correction type {correction_type} selected.")
        for container, image_path in self.thumbnails:
            if container.findChild(QCheckBox).isChecked():
                self.apply_correction(image_path, correction_type)

    def apply_correction(self, image_path, correction_type):
        image = Image.open(image_path)
        output_dir = os.path.join(os.path.dirname(image_path), "processed")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(image_path))
        
        if correction_type == 1:  
            enhancer = ImageEnhance.Brightness(image)
            enhanced_image = enhancer.enhance(self.brightness_slider.value() / 100.0)
        
        elif correction_type == 2: 
            processor = ImageProcessing(image_path)
            enhanced_image = Image.fromarray(processor.unify_exposure())
        
        elif correction_type == 3: 
            enhancer = ImageEnhance.Color(image)
            enhanced_image = enhancer.enhance(self.color_slider.value() / 100.0)
        
        elif correction_type == 4: 
            processor = ImageProcessing(image_path)
            enhanced_image = Image.fromarray(processor.horizontal_correction_no_crop())
        
        elif correction_type == 5: 
            processor = ImageProcessing(image_path)
            enhanced_image = Image.fromarray(processor.horizontal_correction_crop())
        
        elif correction_type == 6: 
            aspect_ratio = 16 / 9 
            processor = ImageProcessing(image_path)
            enhanced_image = Image.fromarray(processor.crop_with_aspect_ratio(aspect_ratio))
        
        elif correction_type == 7: 
            processor = ImageProcessing(image_path)
            blur_score = processor.evaluate_blur()
            print(f"Image blur score: {blur_score}")
            enhanced_image = image 
        
        elif correction_type == 8:
            processor = ImageProcessing(image_path)
            if not processor.filter_closed_eyes():
                print("Image skipped due to closed eyes.")
            enhanced_image = image
        
        elif correction_type == 9:
            processor = ImageProcessing(image_path)
            overlap_score = processor.detect_face_overlap()
            if overlap_score > 0:  
                print("Image skipped due to face overlap.")
            enhanced_image = image
        else:  
            print("Unrecognized correction type. Returning original image.")
            enhanced_image = image

        enhanced_image.save(output_path)
        print(f"Processed image saved to: {output_path}")


    def unify_exposure(self, image):
        image_cv = np.array(image)
        lab = cv2.cvtColor(image_cv, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        merged = cv2.merge((cl, a, b))
        return Image.fromarray(cv2.cvtColor(merged, cv2.COLOR_LAB2RGB))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        self.add_images(files)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageApp()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())

