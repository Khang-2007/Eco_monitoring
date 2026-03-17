import time
import requests
from Adafruit_IO import Client, Feed

# 1. CẤU HÌNH ADAFRUIT IO (Thay bằng thông tin của bạn)
ADAFRUIT_IO_USERNAME = 'VGU_pj'
ADAFRUIT_IO_KEY = 'aio_nJQN89MPqh1kFJvF9gbZNQ37UFY6'

aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# 2. CẤU HÌNH API THỜI TIẾT (Từ bài trước)
API_TOKEN = '5cc015e8e495db3d1fdd839bafb7084067db387b'
CITY_SLUG = 'hanoi'

def get_env_data():
    url = f"https://api.waqi.info/feed/{CITY_SLUG}/?token={API_TOKEN}"
    try:
        response = requests.get(url, verify=False)
        data = response.json()
        if data['status'] == 'ok':
            result = data['data']
            return {
                "aqi": result.get('aqi', 0),
                "temp": result['iaqi'].get('t', {}).get('v', 0),
                "humidity": result['iaqi'].get('h', {}).get('v', 0)
            }
    except Exception as e:
        print("Lỗi lấy dữ liệu:", e)
    return None

# 3. VÒNG LẶP IOT: LẤY DỮ LIỆU VÀ GỬI LÊN MQTT
print("Đang khởi động trạm IoT ảo...")

while True:
    print("-" * 30)
    data = get_env_data()
    
    if data:
        print(f"Đã lấy dữ liệu: Nhiệt độ: {data['temp']}°C | Độ ẩm: {data['humidity']}% | AQI: {data['aqi']}")
        
        try:
            # Gửi dữ liệu lên các Feed tương ứng trên Adafruit IO
            # Lưu ý: Tên feed trong ngoặc kép phải giống y hệt tên bạn tạo trên web
            aio.send('nhiet-do', data['temp'])
            aio.send('do-am', data['humidity'])
            aio.send('chat-luong-khong-khi', data['aqi'])
            
            print("🚀 Đã Publish thành công lên Adafruit IO Dashboard!")
        except Exception as e:
            print("Lỗi khi gửi lên MQTT:", e)
            
    # Nghỉ 10 giây rồi gửi tiếp (Để tránh bị khóa tài khoản miễn phí)
    time.sleep(10)