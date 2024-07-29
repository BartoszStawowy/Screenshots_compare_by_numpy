import os
import numpy as np
import pprint
from PIL import Image
from src.base_page.base_page import BasePage


class ScreenshotComparator(BasePage):

    """
    This class is responsible for compare images. To add a new element to compare, add a locator with element name in
    proper  class, as element of dict.
    dict = {locator: (By.XPATH, '//div[@class="element_class_name"]
    
    Captured image will be automatically add to screenshot folder and compare with previously added
    image(image should be added by user to proper baseline folder with the same name as class or id of element
    in locators dict.

    In this class, U HAVE TO SET PROPER PATHS TO IMAGES FOLDERS
    """

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    threshold = 0.1

    def get_list_of_images(self, folder_path):
        return [f for f in os.listdir(f'{self.project_root}/{folder_path}') if f.lower().endswith('.png')]

    def compare_lists(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        common_elements = list(set1.intersection(set2))
        different_elements = list(set1.symmetric_difference(set2))
        if different_elements != []:
            pprint.pprint(f'Elements that are not in both folders(screenshots and baseline, cant be compared): '
                  f'{different_elements}')
        return common_elements, different_elements

    def compare_elements_in_folders(self, screenshots_path_folder, baseline_path_folder):
        screenshots_list = self.get_list_of_images(screenshots_path_folder)
        images_list = self.get_list_of_images(baseline_path_folder)
        common_images, others = self.compare_lists(screenshots_list, images_list)
        return common_images, others


    def resize_images(self, img1, img2):
        """Resize images to match the larger of the two."""
        max_width = max(img1.width, img2.width)
        max_height = max(img1.height, img2.height)
        img1 = img1.resize((max_width, max_height), Image.LANCZOS)
        img2 = img2.resize((max_width, max_height), Image.LANCZOS)
        return img1, img2

    def compare_screenshots(self, baseline_folder, screenshot_folder, common_images):
        results = []

        for image_name in common_images:
            baseline_path = f'{self.project_root}/{os.path.join(baseline_folder, image_name)}'
            screenshot_path = f'{self.project_root}/{os.path.join(screenshot_folder, image_name)}'

            if not os.path.exists(baseline_path):
                results.append((image_name, False, 100, "Baseline not found"))
                continue

            if not os.path.exists(screenshot_path):
                results.append((image_name, False, 100, "Screenshot not found"))
                continue

            try:
                baseline_image = Image.open(baseline_path).convert('RGB')
                current_image = Image.open(screenshot_path).convert('RGB')

                if current_image.size != baseline_image.size:
                    current_image, baseline_image = self.resize_images(current_image, baseline_image)

                current_array = np.array(current_image)
                baseline_array = np.array(baseline_image)

                diff_array = np.abs(current_array - baseline_array)
                diff_percentage = np.sum(diff_array) / (current_array.size * 255) * 100
                is_match = round(float(diff_percentage), 2) <= self.threshold

                results.append((image_name, is_match, f'diff percentage: {round(float(diff_percentage), 2)}', ""))

            except Exception as e:
                results.append((image_name, False, 100, f"Error: {str(e)}"))
        pprint.pprint(results)
        return results
