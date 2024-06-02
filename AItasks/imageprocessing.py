import cv2
import supervision as sv
import os
from tqdm import tqdm
from ultralytics import YOLO

def extract_keywords_from_image(image):
    """
    Extract keywords from an image using YOLO model and count the occurrences of each keyword.
    @param image - the image to extract keywords from
    @return A dictionary containing the count of each keyword extracted from the image.
    """
    image = cv2.imread(image)
    model = YOLO("yolov8n-oiv7.pt")
    results = model(image)
    keyword_counts = {} 
    for result in results:
        boxes = result.boxes  
        masks = result.masks  
        keypoints = result.keypoints
        probs = result.probs 
        for item in result.boxes.cls:
            item = int(item.item()) 
            if item in result.names:
                keyword = result.names[item]
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    return keyword_counts