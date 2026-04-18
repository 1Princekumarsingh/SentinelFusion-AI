import torch 
import cv2

class DepthEstimator:
    def __init__(self):
        self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        self.model.eval()

        self.transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
    
    def predict(self, frame):
        small = cv2.resize(frame, (256, 256))
        
        img = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        input_batch = self.transform(img)

        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=frame.shape[:2],
                mode="bicubic",
                align_corners=False
            ).squeeze()

        depth_map = prediction.cpu().numpy()
        return depth_map       