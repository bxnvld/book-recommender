import json
import numpy as np
import os

class BookRecommender:
    def __init__(self, meta_path="data/books_prepared.json", emb_path="data/book_embeddings_projected.npy"):
        print("Loading recommender system...")
        
        # 1. Завантаження метаданих
        if not os.path.exists(meta_path):
             # Fallback, якщо prepared не існує
             meta_path = "data/books_meta.json"
        
        with open(meta_path, "r", encoding="utf-8") as f:
            self.books = json.load(f)
            
        # 2. Завантаження векторів
        self.embs = np.load(emb_path)
        
        # 3. Нормалізація (щоб dot product = cosine similarity)
        norm = np.linalg.norm(self.embs, axis=1, keepdims=True)
        self.embs = self.embs / (norm + 1e-9)
        
        # 4. Словник для швидкого пошуку за назвою
        self.title_to_idx = {b.get('title', '').lower(): i for i, b in enumerate(self.books)}
        
        print(f"Loaded {len(self.books)} books.")

    def search(self, query):
        """Знайти індекс книги за назвою (простий пошук підрядка)"""
        query = query.lower()
        results = []
        for i, book in enumerate(self.books):
            if query in book.get('title', '').lower():
                results.append(i)
        return results[:5] # Повернути перші 5 збігів

    def recommend(self, book_idx, k=5):
        """Рекомендації за індексом книги (векторний пошук)"""
        if book_idx >= len(self.embs):
            return []
            
        query_vec = self.embs[book_idx]
        scores = np.dot(self.embs, query_vec)
        
        # Сортуємо (від найбільшого до найменшого)
        top_indices = np.argsort(scores)[::-1]
        
        recommendations = []
        seen_titles = set()
        
        # Додаємо поточну книгу в seen, щоб не рекомендувати її саму
        current_title = self.books[book_idx].get('title', '').strip().lower()
        seen_titles.add(current_title)
        
        for idx in top_indices:
            if len(recommendations) >= k:
                break
                
            book = self.books[idx]
            title = book.get('title', 'Unknown').strip()
            title_lower = title.lower()
            
            # Фільтр дублікатів
            if title_lower in seen_titles:
                continue
            
            seen_titles.add(title_lower)
            
            recommendations.append({
                "title": title,
                "author": book.get("author", "Unknown"),
                "year": book.get("year", ""),
                "score": float(scores[idx]),
                "synopsis": book.get("synopsis", "")[:200] + "..." if book.get("synopsis") else ""
            })
            
        return recommendations

# --- TEST ---
if __name__ == "__main__":
    rec = BookRecommender()
    
    # Тест: знайдемо Арістотеля
    search_res = rec.search("Ethics")
    if search_res:
        idx = search_res[0] # Беремо першу знайдену
        print(f"\nRecommending for: {rec.books[idx]['title']}")
        
        res = rec.recommend(idx)
        for r in res:
            print(f" -> {r['title']} ({r['score']:.2f})")
