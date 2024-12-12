import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout, QCheckBox,
    QPushButton, QSlider, QFileDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QMimeData
from PIL import Image, ImageEnhance

class ImageApp(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()

        correction_buttons_layout = QHBoxLayout()
        
        overview_frame = QWidget()
        overview_frame.setStyleSheet("background-color: #9bf28a; padding: 10px; margin-left: 50px; margin-right: 30px;")  # Green background
        overview_buttons_layout = QVBoxLayout(overview_frame)

        options = ["補正系", "トリミング系", "選定系", "その他"]
        for option in options:
            button = QPushButton(option)
            button.setStyleSheet("""
                font-size: 18px; 
                font-weight: bold; 
                padding: 5px; 
                background-color: transparent;  /* Make button background transparent */
            """)
            overview_buttons_layout.addWidget(button)

        correction_buttons_layout.addWidget(overview_frame)

        main_button_layout = QVBoxLayout()

        first_row_layout = QHBoxLayout()
        options = ["①全体の露出補正", "②手前と奥の露出統一", "③色補正"]

        self.countselect = 0 

        for option in options:
            button = QPushButton(option)
            button.setStyleSheet("""
                font-size: 16px;
                background-color: #ADD8E6;
                padding: 5px;
                margin: 2px;
                margin-right: 20px;
            """)

            if option == "①全体の露出補正":
                button.clicked.connect(self.toggle_select_deselect)

            # elif option == "②手前と奥の露出統一":
            #     button.clicked.connect(self.unify_exposure)  # Connect to the specific handler
            # elif option == "③色補正":
            #     button.clicked.connect(self.color_correction)  # Connect to the specific handler

            first_row_layout.addWidget(button)
            first_row_layout.setStretch(first_row_layout.indexOf(button), 1)

        main_button_layout.addLayout(first_row_layout)

        second_row_layout = QHBoxLayout()
        options = ["④水平補正(人物を切らない)", "⑤水平補正(人物を切る)", "⑥トリミング"]

        for option in options:
            button = QPushButton(option)
            button.setStyleSheet("""
                font-size: 16px;
                background-color: #FFFF00;  /* Yellow background */
                padding: 5px;                 /* Padding inside the button */
                margin: 2px;                  /* Margin around the button */
                margin-right: 20px;
            """)
            # button.clicked.connect(self.handle_second_row_buttons)  # Connect to handler
            second_row_layout.addWidget(button)
            second_row_layout.setStretch(second_row_layout.indexOf(button), 1)

        main_button_layout.addLayout(second_row_layout)

        third_row_layout = QHBoxLayout() 
        options = ["⑦ブレ、ピンボケ", "⑧目瞑り", "⑨顔の重なり", "⑩類似写真"]
        

        for option in options:
            button = QPushButton(option)
            button.setStyleSheet("""
                font-size: 16px;
                background-color: #FFCCCB;  /* Light red background */
                padding: 5px;                 /* Padding inside the button */
                margin: 2px;                  /* Margin around the button */
                margin-right: 20px;
            """)
            # button.clicked.connect(self.handle_third_row_buttons)
            third_row_layout.addWidget(button)
            third_row_layout.setStretch(third_row_layout.indexOf(button), 1)
        main_button_layout.addLayout(third_row_layout)

        forth_row_layout = QHBoxLayout() 
        button = QPushButton("解像度")
        button.setStyleSheet("""
                font-size: 16px;
                background-color: #f29b0f; 
                padding: 5px;               
                margin: 2px;                  
                margin-right: 20px;
            """)
        button.setFixedWidth(int(self.width()))
        forth_row_layout.addWidget(button, alignment=Qt.AlignLeft)
        main_button_layout.addLayout(forth_row_layout)
        correction_buttons_layout.addLayout(main_button_layout)
        self.main_layout.addLayout(correction_buttons_layout)
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

        self.setLayout(self.main_layout)
        self.setWindowTitle("色補正アプリ")

        self.create_footer()
        self.image_paths = []
        self.thumbnails = []

        self.setAcceptDrops(True)

    def add_images(self, files):
        for file in files:
            if os.path.isfile(file):
                self.image_paths.append(file) 
        self.update_grid_layout()

    def update_grid_layout(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for index, image_path in enumerate(self.image_paths):
            row = index // 4
            col = index % 4

            self.display_thumbnail(image_path, row, col)

    def display_thumbnail(self, image_path, row, col):
        frame = QFrame()
        frame.setFixedSize(400, 450)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0; 
                border: 1px solid #d1d1d1; 
                border-radius: 10px; 
                padding: 10px; 
                margin: 10px;
            }
        """)

        pixmap = QPixmap(image_path).scaled(380, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setStyleSheet("border:none;")
        image_label.setAlignment(Qt.AlignCenter)

        file_name_label = QLabel(os.path.basename(image_path))
        file_name_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        file_name_label.setAlignment(Qt.AlignCenter)

        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(5)
        checkbox_layout.setAlignment(Qt.AlignCenter)

        number_layout = QHBoxLayout()
        number_layout.setSpacing(1)
        number_layout.setAlignment(Qt.AlignCenter)

        options = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]

        for option in options:
            checkbox = QCheckBox()
            checkbox.setStyleSheet("margin: 0 5px;")
            checkbox_layout.addWidget(checkbox)

            label = QLabel(option)
            label.setStyleSheet("margin:3.4px; padding:2px; font-size:15px; border:none;")
            number_layout.addWidget(label)

        # Arrange the layout vertically
        image_widget = QVBoxLayout()
        image_widget.setSpacing(10)
        image_widget.setContentsMargins(0, 0, 0, 0)  
        image_widget.addWidget(image_label)
        image_widget.addWidget(file_name_label)
        image_widget.addLayout(checkbox_layout)
        image_widget.addLayout(number_layout)

        frame.setLayout(image_widget)

        self.grid_layout.addWidget(frame, row, col)
        self.thumbnails.append((frame, image_path))

    def select_all(self):
        for container, _ in self.thumbnails:
            for checkbox in container.findChildren(QCheckBox):
                checkbox.setChecked(True)

    def deselect_all(self):
        for container, _ in self.thumbnails:
            for checkbox in container.findChildren(QCheckBox):
                checkbox.setChecked(False)

    def process_images(self):
        brightness_factor = self.brightness_slider.value() / 100.0
        for container, image_path in self.thumbnails:
            if any(cb.isChecked() for cb in container.findChildren(QCheckBox)):
                self.apply_brightness(image_path, brightness_factor)

    def apply_brightness(self, image_path, factor):
        image = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(image)
        enhanced_image = enhancer.enhance(factor)
        output_dir = os.path.join(os.path.dirname(image_path), "processed")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(image_path))
        enhanced_image.save(output_path)
        print(f"Saved processed image to: {output_path}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        self.add_images(files)

    def toggle_select_deselect(self):
        if self.countselect == 0:
            self.select_all()  
            self.countselect = 1 
        else:
            self.deselect_all() 
            self.countselect = 0  
    
    def create_sliders(self):
        sliders_layout = QVBoxLayout()

        self.brightness_slider = self.create_slider("明るさ", sliders_layout)

        self.contrast_slider = self.create_slider("コントラスト", sliders_layout)

        self.saturation_slider = self.create_slider("色濃度", sliders_layout)

        self.exposure_slider = self.create_slider("色かぶり", sliders_layout)

        self.main_layout.addLayout(sliders_layout)

    def create_slider(self, label_text, parent_layout):
        slider_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px; padding-right: 10px;")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(-100, 100)
        slider.setValue(0)
        slider_layout.addWidget(label)
        slider_layout.addWidget(slider)
        parent_layout.addLayout(slider_layout)
        return slider
    def create_footer(self):
        footer_layout = QVBoxLayout()
        sliders_layout = QGridLayout()
        sliders_layout.setHorizontalSpacing(40)
        sliders_layout.setVerticalSpacing(20)
        sliders = [
            ("露出補正", "brightness_slider"),
            ("コントラスト", "contrast_slider"),
            ("色温度", "temperature_slider"),
            ("色かぶり", "exposure_slider"),
            ("自然な彩度", "natural_saturation_slider"),
            ("彩度", "saturation_slider"),
        ]

        for i, (label_text, attr_name) in enumerate(sliders):
            slider_block = QVBoxLayout()
            slider_block.setSpacing(5)

            label = QLabel(label_text)
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet("font-size: 15px; font-weight:800")

            value_display = QLabel("-14") 
            value_display.setAlignment(Qt.AlignLeft)
            value_display.setStyleSheet("font-size: 12px; color: gray;")

            slider_layout = QHBoxLayout()

            min_label = QLabel("-100")
            min_label.setStyleSheet("font-size: 12px; color: gray;")
            min_label.setAlignment(Qt.AlignCenter)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(-100, 100)
            slider.setValue(-14)
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(20)  
            setattr(self, attr_name, slider)

            slider.valueChanged.connect(lambda value, display=value_display: display.setText(str(value)))

            max_label = QLabel("100")
            max_label.setStyleSheet("font-size: 12px; color: gray;")
            max_label.setAlignment(Qt.AlignCenter)

            slider_layout.addWidget(min_label)
            slider_layout.addWidget(slider)
            slider_layout.addWidget(max_label)

            slider_block.addWidget(label)
            slider_block.addWidget(value_display)
            slider_block.addLayout(slider_layout)

            row, col = divmod(i, 4)  
            sliders_layout.addLayout(slider_block, row, col)

        footer_layout.addLayout(sliders_layout)

        execute_button = QPushButton("実 行")
        execute_button.setStyleSheet("""
            font-size: 30px; 
            font-weight: 800; 
            padding: 10px; 
            color: white;  
            margin-right:40px;
            background-color: #0303fc;  
        """)

        execute_button.setMinimumHeight(50)
        footer_layout.addWidget(execute_button, alignment=Qt.AlignRight)

        self.main_layout.addLayout(footer_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageApp()
    window.resize(1800, 1000)
    window.show()
    sys.exit(app.exec_())