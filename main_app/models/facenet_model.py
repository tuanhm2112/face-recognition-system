"""
FaceNet Model - Face Recognition sử dụng InceptionResnetV1
"""
import torch
from facenet_pytorch import InceptionResnetV1

class FaceNetModel:
    """Wrapper class cho FaceNet model"""
    
    def __init__(self, device='cuda', pretrained='vggface2'):
        """
        Khởi tạo FaceNet model
        
        Args:
            device: 'cuda' hoặc 'cpu'
            pretrained: 'vggface2' hoặc 'casia-webface'
        """
        # Safe CUDA check
        try:
            use_cuda = device == 'cuda' and torch.cuda.is_available()
        except:
            use_cuda = False
        self.device = torch.device('cuda' if use_cuda else 'cpu')
        self.model = InceptionResnetV1(pretrained=pretrained).eval().to(self.device)
    
    def extract_embedding(self, face_tensor):
        """
        Trích xuất embedding từ face tensor
        
        Args:
            face_tensor: Tensor kích thước (N, 3, 160, 160)
            
        Returns:
            Embedding vector (N, 512)
        """
        with torch.no_grad():
            embedding = self.model(face_tensor)
        return embedding
    
    def __call__(self, face_tensor):
        """Cho phép gọi trực tiếp như function"""
        return self.extract_embedding(face_tensor)
