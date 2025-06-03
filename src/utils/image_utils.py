def load_image(image_path):
    import cv2
    image = cv2.imread(image_path)
    return image

def save_image(image, save_path):
    import cv2
    cv2.imwrite(save_path, image)

def preprocess_image(image, target_size=(224, 224)):
    import cv2
    image = cv2.resize(image, target_size)
    image = image / 255.0  # Normalize to [0, 1]
    return image