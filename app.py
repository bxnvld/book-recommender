# from flask import Flask, render_template, request, jsonify
# from recommender_class import BookRecommender # Перевірте, чи файл називається саме так, або recommender_class

# app = Flask(__name__)

# # --- ІНІЦІАЛІЗАЦІЯ МОДЕЛІ ---
# # Завантажуємо модель один раз при старті
# # Переконайтесь, що шляхи правильні
# try:
#     print("Loading Recommender System...")
#     # Тут ми ініціалізуємо клас, який ви використовували в api.py
#     # Якщо він потребує аргументів (шляхи до файлів), додайте їх сюди
#     rec = BookRecommender() 
#     print("Model loaded successfully.")
# except Exception as e:
#     print(f"ERROR loading model: {e}")
#     rec = None

# # --- МАРШРУТИ (ROUTES) ---

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/search")
# def search():
#     query = request.args.get("q", "").strip()
    
#     if not query or not rec:
#         return render_template("partials/book_list.html", books=[])

#     # Використовуємо логіку пошуку з вашого класу
#     indices = rec.search(query)
#     results = []
    
#     # Припускаю, що rec.books - це список словників або об'єктів
#     # Адаптуйте цей цикл під структуру вашого BookRecommender
#     for i in indices:
#         # Перевірка меж масиву
#         if i < len(rec.books):
#             b = rec.books[i]
#             # Flask шаблони люблять словники
#             results.append({
#                 "id": i,
#                 "title": b.get("title", "Unknown"),
#                 "author": b.get("author", "Unknown")
#             })

#     # Повертаємо тільки шматочок HTML для HTMX
#     return render_template("partials/book_list.html", books=results)

# @app.route("/recommend")
# def recommend():
#     try:
#         book_id = int(request.args.get("id"))
        
#         # Отримуємо рекомендації (адаптуйте під ваш клас)
#         recommendations = rec.recommend(book_id, k=5)
        
#         # Повертаємо шматочок HTML
#         return render_template("partials/recommendations.html", books=recommendations)
#     except Exception as e:
#         print(f"Error: {e}")
#         return '<div class="text-red-500">Error generating recommendations</div>', 500

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)


import os
import zipfile
from flask import Flask, render_template, request
from recommender_class import BookRecommender

app = Flask(__name__)

# --- АВТОМАТИЧНЕ РОЗПАКУВАННЯ ---
def unzip_if_needed(zip_path, target_file):
    # Розпаковуємо, якщо є архів, але немає цільового файлу
    if os.path.exists(zip_path) and not os.path.exists(target_file):
        print(f"📦 Found {zip_path}. Unzipping to data/...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("data")
            print(f"✅ Extracted {target_file}")
        except Exception as e:
            print(f"❌ Error unzipping {zip_path}: {e}")

# Перевіряємо обидва архіви
unzip_if_needed("data/z_emb.zip", "data/book_embeddings.npy")
unzip_if_needed("data/z_meta.zip", "data/books_meta.json")

# --- ІНІЦІАЛІЗАЦІЯ МОДЕЛІ ---
try:
    print("Loading AI Model...")
    rec = BookRecommender(
        # projected.npy малий (50МБ), він летить як є
        emb_path="data/book_embeddings_projected.npy", 
        # meta.json розпакується з архіву
        meta_path="data/books_meta.json"
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load model. {e}")
    rec = None

# ... ДАЛІ ВАШ КОД БЕЗ ЗМІН ...

# --- ГОЛОВНА СТОРІНКА ---
@app.route("/")
def index():
    return render_template("index.html")

# --- ПОШУК (HTMX) ---
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    
    # Якщо модель не завантажилась або запит пустий
    if not rec or len(query) < 2:
        return "" 

    try:
        indices = rec.search(query)
        html_response = ""

        # Генеруємо HTML список прямо тут (як це робив Go)
        for i in indices:
            if i < len(rec.books):
                b = rec.books[i]
                title = b.get("title", "Unknown")
                author = b.get("author", "Unknown")
                
                html_response += f"""
                <div class="p-3 bg-slate-800 rounded-lg hover:bg-slate-700 cursor-pointer transition border border-slate-700 flex justify-between items-center group"
                     hx-get="/recommend?id={i}"
                     hx-target="#recommendations-container"
                     hx-swap="innerHTML">
                    <div>
                        <div class="font-bold text-lg group-hover:text-blue-300">{title}</div>
                        <div class="text-sm text-slate-400">{author}</div>
                    </div>
                    <span class="text-2xl text-slate-600 group-hover:text-blue-400">→</span>
                </div>
                """
        
        if not html_response:
            return '<div class="text-slate-500">No books found.</div>'
            
        return html_response

    except Exception as e:
        print(f"Search error: {e}")
        return '<div class="text-red-500">Search error</div>'

# --- РЕКОМЕНДАЦІЇ (HTMX) ---
@app.route("/recommend")
def recommend():
    try:
        book_id = int(request.args.get("id"))
        recommendations = rec.recommend(book_id, k=5)
        
        html_response = ""
        for book in recommendations:
            title = book.get("title", "")
            author = book.get("author", "")
            synopsis = book.get("synopsis", "") or ""
            image_url = book.get("image_url", "")
            score = book.get("score", 0) * 100
            
            # Блок картинки
            img_html = ""
            if image_url:
                img_html = f'<div class="w-24 h-auto flex-shrink-0"><img src="{image_url}" class="w-full h-full object-cover"></div>'

            html_response += f"""
            <div class="flex bg-slate-800 rounded-xl border-l-4 border-emerald-500 shadow-md animate-fade-in overflow-hidden mb-4">
                {img_html}
                <div class="p-4 flex-1">
                    <h3 class="font-bold text-lg text-emerald-300">{title}</h3>
                    <p class="text-sm text-slate-300 mb-2">by {author}</p>
                    <p class="text-xs text-slate-400 line-clamp-3">{synopsis}</p>
                    <div class="mt-2 text-xs font-mono text-slate-500 text-right">
                        Match: {score:.1f}%
                    </div>
                </div>
            </div>
            """
            
        return html_response

    except Exception as e:
        return f'<div class="text-red-500">Error: {str(e)}</div>'

if __name__ == "__main__":
    # Render очікує, що ми запустимося, але gunicorn зробить це за нас
    app.run(debug=True)