import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import os

# Tắt các cảnh báo log không cần thiết của TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("[AI] Đang nạp mô hình MobileNetV2... (Có thể mất vài giây)")
model = MobileNetV2(weights='imagenet')
print("[AI] Hệ thống Thị giác Máy tính đã sẵn sàng!")

def is_actually_water(image_path):
    """Lớp 1: Kiểm duyệt nghiêm ngặt chống ảnh giả, ảnh rác"""
    try:
        img = image.load_img(image_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        preds = model.predict(x, verbose=0)
        top_5_results = decode_predictions(preds, top=5)[0]

        # Danh sách ĐỘC QUYỀN các cảnh quan có nước
        WATER_CLASSES = [
            'lakeside', 'seashore', 'breakwater', 'sandbar', 'promontory',
            'dam', 'dock', 'pier', 'coral_reef', 'geyser', 'cliff', 'valley',
            'fountain', 'boathouse', 'canoe', 'gondola', 'paddle'
        ]

        print("\n[AI Vision] Đang bóc tách vật thể trong ảnh:")
        
        for _, class_name, probability in top_5_results:
            class_name = class_name.lower()
            confidence = probability * 100
            
            print(f" ---> Nhìn giống '{class_name}': {confidence:.1f}%")

            # LUẬT THÉP 1: Độ tự tin phải trên 12%
            if confidence >= 12.0:
                # LUẬT THÉP 2: Nằm trong danh sách cảnh quan nước
                if class_name in WATER_CLASSES:
                    return True

                # LUẬT THÉP 3: Cắt riêng từng chữ để tránh bẫy từ vựng
                words = class_name.split('_') 
                if 'water' in words or 'sea' in words or 'lake' in words or 'river' in words or 'ocean' in words:
                    return True

        print("[AI Vision] ❌ CẢNH BÁO: Ảnh này KHÔNG PHẢI cảnh quan nước hợp lệ!")
        return False
        
    except Exception as e:
        print(f"[AI Error] Lỗi hệ thống thị giác: {e}")
        return False

def analyze_water_advanced(image_path):
    """Lớp 3: Cắt phần bầu trời và phân tích quang phổ HSV"""
    img = cv2.imread(image_path)
    if img is None: 
        return {"quality": "Lỗi định dạng ảnh", "color": "Khác"}

    # Cắt 1/3 ảnh phía trên để loại bỏ bầu trời phản chiếu
    height, width = img.shape[:2]
    roi_water = img[int(height/3):height, 0:width] 

    hsv = cv2.cvtColor(roi_water, cv2.COLOR_BGR2HSV)
    avg_h = np.mean(hsv[:,:,0])
    avg_s = np.mean(hsv[:,:,1])
    avg_v = np.mean(hsv[:,:,2])

    if avg_s < 30 or avg_v < 50: return {"quality": "Nước đục/Bóng râm", "color": "Xám/Đen"}
    elif 10 <= avg_h <= 35: return {"quality": "Cảnh báo: Ô nhiễm bùn đất", "color": "Nâu/Vàng"}
    elif 35 < avg_h <= 85: return {"quality": "Cảnh báo: Nhiều tảo/Rêu", "color": "Xanh lục"}
    else: return {"quality": "Tuyệt vời: Nước biển/Hồ trong", "color": "Xanh dương"}