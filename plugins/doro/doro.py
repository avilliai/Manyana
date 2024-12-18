import io
from PIL import Image, ImageSequence
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
import base64
import os

# 定义数据预处理
test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# 加载模型
def load_model(model_path, device):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)  # 修改最后一层为分类层
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model

def predict_frame(frame, model, transform, device):
    """ 对单帧图像进行预测 """
    model.eval()
    frame = transform(frame).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(frame)
        _, pred = torch.max(output, 1)
    return pred.item() == 1  # 返回是否为奶龙元素

def predict_image_or_gif(image_bytes, model, transform, device):
    """ 对图像或GIF文件进行预测 """
    model.eval()
    image_stream = io.BytesIO(image_bytes)
    image = Image.open(image_stream)
    
    if image.format == 'GIF':
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert('RGB')
            if predict_frame(frame, model, transform, device):
                return True  # 发现奶龙元素
        return False  # 没有发现奶龙元素
    else:
        image = image.convert('RGB')
        return predict_frame(image, model, transform, device)  # 返回是否为奶龙元素

def predict_video(video_bytes, model, transform, device):
    """ 对视频文件的每一帧进行预测 """
    video_stream = io.BytesIO(video_bytes)
    cap = cv2.VideoCapture()
    cap.open(video_stream)

    frame_count = 0
    found = False
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        if predict_frame(pil_image, model, transform, device):
            found = True
            print(f"Frame {frame_count}: True")  # 发现奶龙元素
        frame_count += 1
    cap.release()
    if not found:
        print("Prediction: False")  # 没有发现奶龙元素
    return found

def detect_doro_from_base64(base64_string, model, transform, device):
    # 解码base64字符串
    image_bytes = base64.b64decode(base64_string)
    
    # 尝试打开图像以确定其格式
    image_stream = io.BytesIO(image_bytes)
    try:
        image = Image.open(image_stream)
        if image.format in ['JPEG', 'PNG', 'BMP', 'GIF']:
            return predict_image_or_gif(image_bytes, model, transform, device)
    except IOError:
        pass
    
    # 如果不是图像，则尝试作为视频处理
    try:
        return predict_video(image_bytes, model, transform, device)
    except Exception as e:
        print(f"Error processing input: {e}")
        return False

def main(base64_string):
    # 设备
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    # 模型路径（相对于脚本所在目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, 'doro.pth')
    model = load_model(model_path, device)
    
    # 检测奶龙元素
    result = detect_doro_from_base64(base64_string, model, test_transform, device)
    print(f"Detection Result: {'True' if result else 'False'}")
    return result
