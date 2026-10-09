"""
Person Service - Quản lý CRUD operations cho persons
"""
import os
import cv2
import shutil

class PersonService:
    """Service quản lý persons trong hệ thống"""
    
    def __init__(self, recognizer, data_dir="resources/data"):
        """
        Khởi tạo service
        
        Args:
            recognizer: Face recognizer instance
            data_dir: Thư mục chứa dữ liệu persons
        """
        self.recognizer = recognizer
        if not os.path.isabs(data_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            data_dir = os.path.join(project_root, data_dir)
        self.data_dir = data_dir
    
    def add_person(self, name, frames, embeddings):
        """
        Thêm người mới vào hệ thống
        
        Args:
            name: Tên người
            frames: List frames gốc
            embeddings: List embeddings tương ứng
            
        Returns:
            tuple: (success: bool, person_id: str, message: str)
        """
        try:
            # Tạo folder cho person
            person_folder = self._create_person_folder(name)
            
            # Lấy person_id
            identities = self.recognizer.get_identities()
            person_id = str(len(identities))
            
            # Lưu ảnh và embeddings
            saved_count = 0
            for i, (frame, embedding) in enumerate(zip(frames, embeddings)):
                # Lưu ảnh gốc
                original_path = os.path.join(person_folder, f"original_{i}.jpg")
                cv2.imwrite(original_path, frame)
                
                # Thêm embedding vào recognizer
                self.recognizer.add_embedding(embedding, person_id, name)
                saved_count += 1
            
            if saved_count == 0:
                return False, None, "No embeddings saved"
            
            return True, person_id, f"Added '{name}' with {saved_count} photo(s)"
            
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def save_face_images(self, person_name, original_frames, aligned_faces):
        """
        Lưu ảnh gốc và aligned faces
        
        Args:
            person_name: Tên người
            original_frames: List frames gốc
            aligned_faces: List aligned faces
            
        Returns:
            str: Đường dẫn folder đã lưu
        """
        person_folder = self._create_person_folder(person_name)
        
        for i, (original, aligned) in enumerate(zip(original_frames, aligned_faces)):
            cv2.imwrite(f"{person_folder}/original_{i}.jpg", original)
            cv2.imwrite(f"{person_folder}/aligned_{i}.jpg", aligned)
        
        return person_folder
    
    def _create_person_folder(self, name):
        """
        Tạo folder cho person
        
        Args:
            name: Tên người
            
        Returns:
            str: Đường dẫn folder
        """
        folder_name = name.replace(" ", "_").lower()
        person_folder = os.path.join(self.data_dir, "persons", folder_name)
        os.makedirs(person_folder, exist_ok=True)
        return person_folder
    
    def delete_person(self, person_id):
        """
        Xóa người khỏi hệ thống
        
        Args:
            person_id: ID của người cần xóa
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Lấy thông tin person từ recognizer
            identities = self.recognizer.get_identities()
            if person_id not in identities:
                return False, f"Person with ID {person_id} not found"
            
            person_name = identities[person_id]["name"]
            
            # Xóa từ recognizer
            self.recognizer.remove_person(person_id)
            
            # Xóa folder của person
            folder_name = person_name.replace(" ", "_").lower()
            person_folder = os.path.join(self.data_dir, "persons", folder_name)
            if os.path.exists(person_folder):
                shutil.rmtree(person_folder)
            
            return True, f"Person '{person_name}' removed successfully"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_all_persons(self):
        """
        Lấy danh sách tất cả persons
        
        Returns:
            list: Danh sách persons
        """
        return self.recognizer.get_identities()
    
    def validate_person_name(self, name):
        """
        Validate tên người
        
        Args:
            name: Tên cần validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not name or name.strip() == "":
            return False, "Name cannot be empty"
        
        if len(name.strip()) < 2:
            return False, "Name must be at least 2 characters"
        
        # Kiểm tra tên đã tồn tại
        identities = self.recognizer.get_identities()
        for identity in identities.values():
            # identity là dict với key "name" và "embeddings"
            if identity["name"].lower() == name.strip().lower():
                return False, f"Person '{name}' already exists"
        
        return True, ""