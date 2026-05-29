import cv2

def detect_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise Exception("Could not read image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

    if len(faces) == 0:
        # Return full image if no face detected (for camera shots)
        return img

    # Use largest face
    x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
    face_img = img[y:y+h, x:x+w]
    
    # Draw rectangle
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
    marked_path = image_path.replace('uploads', 'results').replace('.', '_marked.')
    cv2.imwrite(marked_path, img)

    return face_img