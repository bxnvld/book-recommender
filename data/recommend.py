import json
import numpy as np
import pickle
from sklearn.neighbors import NearestNeighbors

EMB = "data/book_embeddings_projected.npy"
META = "data/books_meta.json"
INDEX = "models/nn_index.pkl"

print("Loading embeddings...")
emb = np.load(EMB)

print("Loading metadata...")
with open(META, "r", encoding="utf8") as f:
    meta = json.load(f)

print("Loading nearest-neighbors index...")
with open(INDEX, "rb") as f:
    nn = pickle.load(f)

def recommend(book_id, top_k=10):
    vec = emb[book_id].reshape(1, -1)
    dists, idxs = nn.kneighbors(vec, n_neighbors=top_k+1)

    # перший елемент — це сама книга, пропускаємо
    results = []
    for dist, idx in zip(dists[0][1:], idxs[0][1:]):
        info = meta[idx]
        results.append({
            "id": int(idx),
            "title": info.get("title"),
            "authors": info.get("authors"),
            "distance": float(dist)
        })
    return results

# приклад інтерактивного запуску
if __name__ == "__main__":
    while True:
        try:
            x = input("Enter book id (or q): ").strip()
            if x.lower() == "q":
                break
            bid = int(x)

            recs = recommend(bid)
            print("\nRecommendations:\n")
            for r in recs:
                print(f"[{r['id']}] {r['title']} — {r['authors']}  (dist={r['distance']:.4f})")

            print()
        except Exception as e:
            print("Error:", e)
            continue
