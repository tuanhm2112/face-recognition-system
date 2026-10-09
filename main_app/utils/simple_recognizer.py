"""
Simple Face Recognizer using numpy cosine similarity
"""
import os
import json
import numpy as np

class SimpleFaceRecognizer:
    def __init__(self, data_dir, logger):
        self.data_dir = data_dir
        self.logger = logger
        self.identities_path = os.path.join(data_dir, "identities.json")
        self.identities = {}
        self.threshold = 0.6
        
        os.makedirs(data_dir, exist_ok=True)
        self.load_identities()
    
    def load_identities(self):
        """Load identities from JSON file với error handling"""
        try:
            if not os.path.exists(self.identities_path):
                self.identities = {}
                self.save_identities()
                return
            
            # Check file size (max 10MB)
            file_size = os.path.getsize(self.identities_path)
            if file_size == 0:
                self.identities = {}
                self.save_identities()
                return
            if file_size > 10 * 1024 * 1024:
                self.logger.log_warning(f"identities.json quá lớn ({file_size} bytes), resetting...")
                os.rename(self.identities_path, self.identities_path + ".backup")
                self.identities = {}
                self.save_identities()
                return
            
            with open(self.identities_path, 'r', encoding='utf-8') as f:
                self.identities = json.load(f)
        except json.JSONDecodeError as e:
            self.logger.log_error(f"identities.json corrupted: {e}, resetting...")
            if os.path.exists(self.identities_path):
                os.rename(self.identities_path, self.identities_path + ".corrupted")
            self.identities = {}
            self.save_identities()
        except Exception as e:
            self.logger.log_error(f"Error loading identities: {e}")
            self.identities = {}
    
    def save_identities(self):
        """Save identities to JSON file"""
        try:
            with open(self.identities_path, 'w') as f:
                json.dump(self.identities, f, indent=2)
        except Exception as e:
            self.logger.log_error(f"Error saving identities: {e}")
    
    def add_embedding(self, embedding, person_id, name):
        """Add new embedding for person"""
        try:
            vec = np.asarray(embedding, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            else:
                return False
            
            pid = str(person_id)
            if pid not in self.identities:
                self.identities[pid] = {"name": name, "embeddings": []}
            
            self.identities[pid]["name"] = name
            self.identities[pid]["embeddings"].append(vec.tolist())
            
            self.save_identities()
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error adding embedding: {e}")
            return False
    
    def search(self, embedding, threshold=None):
        try:
            if threshold is None:
                threshold = self.threshold
            
            vec = np.asarray(embedding, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            else:
                return "Unknown", 0.0
            
            best_similarity = -1.0
            best_person = "Unknown"
            
            for pid, info in self.identities.items():
                person_name = info.get("name", "Unknown")
                embeddings = info.get("embeddings", [])
                
                for stored_emb in embeddings:
                    stored_vec = np.array(stored_emb, dtype=np.float32)
                    similarity = np.dot(vec, stored_vec)
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_person = person_name
            
            # Trả về cả tên và confidence score
            if best_similarity >= threshold:
                return best_person, best_similarity
            else:
                return "Unknown", best_similarity
                
        except Exception as e:
            self.logger.log_error(f"Error in search: {e}")
            return "Unknown", 0.0
    
    def get_identities(self):
        """Get all identities"""
        return self.identities.copy()
    
    def reload_database(self):
        """Reload database from file"""
        self.load_identities()
    
    def set_threshold(self, threshold):
        """Set similarity threshold"""
        self.threshold = threshold
    
    def remove_person(self, person_id):
        try:
            pid = str(person_id)
            if pid in self.identities:
                del self.identities[pid]
                self.save_identities()
                self.logger.log_info(f"Person {pid} removed from identities")
                return True
            else:
                self.logger.log_warning(f"Person {pid} not found in identities")
                return False
        except Exception as e:
            self.logger.log_error(f"Error removing person {pid}: {e}")
            return False