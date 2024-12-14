import cv2
import numpy as np
from PIL import Image
from math import atan2, degrees



class ImageProcessing:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)

    def horizontal_correction_no_crop(self):
        angle = self.detect_skew_angle()
        if angle:
            h, w = self.image.shape[:2]
            rotation_matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1)
            rotated = cv2.warpAffine(self.image, rotation_matrix, (w, h))
            rotated = self.add_padding(rotated, angle)
            return rotated
        return self.image

    def horizontal_correction_crop(self):
        angle = self.detect_skew_angle()
        if angle:
            h, w = self.image.shape[:2]
            rotation_matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1)
            rotated = cv2.warpAffine(self.image, rotation_matrix, (w, h))
            return self.crop_to_rectangle(rotated, angle)
        return self.image

    def detect_skew_angle(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        angles = []
        if lines is not None:
            for rho, theta in lines[:, 0]:
                angle = np.degrees(theta) - 90
                angles.append(angle)
            return np.median(angles)
        return 0

    def add_padding(self, image, angle):
        h, w = image.shape[:2]
        diagonal = int((h**2 + w**2)**0.5)
        padded = cv2.copyMakeBorder(image, diagonal, diagonal, diagonal, diagonal, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        center = (padded.shape[1] // 2, padded.shape[0] // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
        result = cv2.warpAffine(padded, rotation_matrix, (padded.shape[1], padded.shape[0]))
        return result

    def crop_to_rectangle(self, image, angle):
        h, w = image.shape[:2]
        diagonal = int((h**2 + w**2)**0.5)
        x = int((diagonal - w) / 2)
        y = int((diagonal - h) / 2)
        return image[y:y + h, x:x + w]

    def crop_with_aspect_ratio(self, aspect_ratio):
        h, w = self.image.shape[:2]
        new_w = int(aspect_ratio * h) if aspect_ratio > 1 else w
        new_h = int(w / aspect_ratio) if aspect_ratio < 1 else h
        x = (w - new_w) // 2
        y = (h - new_h) // 2
        cropped = self.image[y:y + new_h, x:x + new_w]
        return cropped

    def evaluate_blur(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        return variance

    @staticmethod
    def find_least_blurry(images):
        scores = [(img, ImageProcessing(img).evaluate_blur()) for img in images]
        return max(scores, key=lambda x: x[1])[0]

    def filter_closed_eyes(self, eye_classifier_path="haarcascade_eye.xml"):
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + eye_classifier_path)
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        return len(eyes) > 0

    @staticmethod
    def remove_closed_eyes(images):
        results = []
        for img_path in images:
            processor = ImageProcessing(img_path)
            if processor.filter_closed_eyes():
                results.append(img_path)
        return results if results else [ImageProcessing.find_least_blurry(images)]

    def detect_face_overlap(self, face_classifier_path="haarcascade_frontalface_default.xml"):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + face_classifier_path)
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        overlap_score = 0
        for (x, y, w, h) in faces:
            overlap_score += w * h 
        return overlap_score

    @staticmethod
    def remove_face_overlap(images):
        scores = [(img, ImageProcessing(img).detect_face_overlap()) for img in images]
        scores.sort(key=lambda x: x[1]) 
        return [img for img, score in scores if score == scores[0][1]]

    @staticmethod
    def find_best_quality(images):
        scores = []
        for img in images:
            processor = ImageProcessing(img)
            blur_score = processor.evaluate_blur()
            resolution = processor.image.shape[0] * processor.image.shape[1]
            scores.append((img, blur_score + resolution))
        return max(scores, key=lambda x: x[1])[0]

    def enhance_resolution(self):
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel("EDSR_x4.pb") 
        sr.setModel("edsr", 4) 
        result = sr.upsample(self.image)
        return result
    
    def global_exposure_correction(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        corrected = cv2.equalizeHist(gray)
        return cv2.merge([corrected] * 3)

    def foreground_background_unification(self):
        lab = cv2.cvtColor(self.image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        unified = cv2.merge((l, a, b))
        return cv2.cvtColor(unified, cv2.COLOR_LAB2BGR)

    def color_correction(self):
        result = cv2.cvtColor(self.image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(result)
        l = cv2.equalizeHist(l)
        corrected = cv2.merge((l, a, b))
        return cv2.cvtColor(corrected, cv2.COLOR_LAB2BGR)

    def horizontal_correction(self, crop=False):
        angle = self.detect_skew_angle()
        if angle:
            h, w = self.image.shape[:2]
            rotation_matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1)
            rotated = cv2.warpAffine(self.image, rotation_matrix, (w, h))
            if crop:
                return self.crop_to_rectangle(rotated, angle)
            else:
                return self.add_padding(rotated, angle)
        return self.image
    
    def horizontal_correction_without_cutting_people(self):
        angle = self.detect_skew_angle()
        if angle:
            h, w = self.image.shape[:2]
            rotation_matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1)
            rotated = cv2.warpAffine(self.image, rotation_matrix, (w, h))

            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            gray_rotated = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_rotated, scaleFactor=1.1, minNeighbors=5)

            if len(faces) > 0:
                face_margins = [
                    (x, y, x + w, y + h)
                    for (x, y, w, h) in faces
                ]
                x_min = min([margin[0] for margin in face_margins])
                y_min = min([margin[1] for margin in face_margins])
                x_max = max([margin[2] for margin in face_margins])
                y_max = max([margin[3] for margin in face_margins])

                pad_top = max(0, -y_min)
                pad_bottom = max(0, y_max - h)
                pad_left = max(0, -x_min)
                pad_right = max(0, x_max - w)

                padded_image = cv2.copyMakeBorder(
                    rotated, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0, 0, 0]
                )
                return padded_image

            return rotated

        return self.image

    def detect_skew_angle(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        angles = []
        if lines is not None:
            for rho, theta in lines[:, 0]:
                angle = np.degrees(theta) - 90
                angles.append(angle)
            return np.median(angles)
        return 0

    def add_padding(self, image, angle):
        h, w = image.shape[:2]
        diagonal = int((h**2 + w**2)**0.5)
        padded = cv2.copyMakeBorder(image, diagonal, diagonal, diagonal, diagonal, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        center = (padded.shape[1] // 2, padded.shape[0] // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
        result = cv2.warpAffine(padded, rotation_matrix, (padded.shape[1], padded.shape[0]))
        return result

    def crop_to_rectangle(self, image, angle):
        h, w = image.shape[:2]
        diagonal = int((h**2 + w**2)**0.5)
        x = int((diagonal - w) / 2)
        y = int((diagonal - h) / 2)
        return image[y:y + h, x:x + w]

    def evaluate_blur(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def enhance_resolution(self):
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel("EDSR_x4.pb")
        sr.setModel("edsr", 4)
        return sr.upsample(self.image)

    def enhance_resolution_with_factor(self, scale_factor):
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        model_path = f"EDSR_x{scale_factor}.pb"
        try:
            sr.readModel(model_path)
            sr.setModel("edsr", scale_factor)
            return sr.upsample(self.image)
        except Exception as e:
            print(f"Error loading model {model_path}: {e}")
            return self.image

