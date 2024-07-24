import os
import io
from PIL import Image
import numpy as np


class ScreenshotComparator:
    def __init__(self, driver, baseline_folder, threshold=0.1):
        self.driver = driver
        self.baseline_folder = baseline_folder
        self.threshold = threshold

    def resize_images(self, img1, img2):
        """Resize images to match the larger of the two."""
        max_width = max(img1.width, img2.width)
        max_height = max(img1.height, img2.height)
        img1 = img1.resize((max_width, max_height), Image.LANCZOS)
        img2 = img2.resize((max_width, max_height), Image.LANCZOS)
        return img1, img2


    def compare_screenshots(self, screenshot, baseline_name):
        """ Specify path to folders(folder with screenshots from page, folder with uploaded images)"""
        baseline_path = os.path.join(self.baseline_folder, baseline_name)
        screenshot_path = os.path.join(self.baseline_folder, screenshot)

        if not os.path.exists(baseline_path):
            raise FileNotFoundError(f"Baseline screenshot not found: {baseline_path}")

        if isinstance(screenshot_path, (str, bytes, io.BytesIO)):
            current_image = Image.open(screenshot_path).convert('RGB')
        else:
            current_image = screenshot.convert('RGB')

        baseline_image = Image.open(baseline_path).convert('RGB')

        if current_image.size != baseline_image.size:
            current_image, baseline_image = self.resize_images(current_image, baseline_image)

        current_array = np.array(current_image)
        baseline_array = np.array(baseline_image)

        diff_array = np.abs(current_array - baseline_array)
        diff_percentage = np.sum(diff_array) / (current_array.size * 255) * 100
        is_match = round(float(diff_percentage), 2) <= self.threshold

        return is_match, round(float(diff_percentage), 2)


        def _generate_filename_from_locator(self, locator):
        import re
        _, xpath = locator
        class_match = re.search(r"@class='([^']*)'", xpath)
        id_match = re.search(r"@id='([^']*)'", xpath)

        if class_match:
            class_name = class_match.group(1)
            filename = re.sub(r'[^\w\-_\. ]', '', class_name).replace(' ', '-')
            return f"{filename}.png"
        elif id_match:
            id_name = id_match.group(1)
            filename = re.sub(r'[^\w\-_\. ]', '', id_name).replace(' ', '-')
            return f"{filename}.png"
        else:
            raise ValueError('Neither class name nor id found.')


    def get_element_screenshot(self, locator, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return element.screenshot_as_png

    def capture_element_screenshot(self, locator, directory):

        element_png = self.get_element_screenshot(locator)
        image = Image.open(io.BytesIO(element_png))

        filename = self._generate_filename_from_locator(locator)
        full_path = os.path.join(directory, filename)

        image.save(full_path)
        return full_path
