from flask import Flask, render_template, request, jsonify, send_file, redirect
import os
import fitz  # PyMuPDF
from PIL import Image
import io

app = Flask(__name__)

# Список книг с добавленным полем class
books = [
    {"id": 1, "title": "Биология 9 класс", "file": "books/biologia9.pdf", "class": "9"},
    {"id": 2, "title": "Русский язык 10 класс", "file": "books/ryssianlesson10.pdf", "class": "10"},
    {"id": 3, "title": "Физика 10 класс: углублённый уровень", "file": "books/fizika10ygl.pdf", "class": "10"},
    {"id": 4, "title": "Химия 10 класс: базовый уровень", "file": "books/himia10baz.pdf", "class": "10"},
    {"id": 5, "title": "Обществознание 10 класс", "file": "books/obshestvo10.pdf", "class": "10"},
    {"id": 6, "title": "Всеобщая история 10 класс", "file": "books/vseobschajaistorija10.pdf", "class": "10"},
    {"id": 7, "title": "История России 10 класс", "file": "books/istorijarossii10.pdf", "class": "10"},
    {"id": 8, "title": "Алгебра 10 класс: базовый и углублённый уровень", "file": "books/algebra10baz_ygl.pdf", "class": "10"},
    {"id": 9, "title": "География 10-11 класс", "file": "books/geografia10-11.pdf", "class": "10"},
    {"id": 9, "title": "География 10-11 класс", "file": "books/geografia10-11.pdf", "class": "11"},
    {"id": 10, "title": "Информатика 10 класс", "file": "books/informatika10.pdf", "class": "10"},
    {"id": 11, "title": "Английский язык 10 класс", "file": "books/angliyskli10.pdf", "class": "10"},
    {"id": 12, "title": "Литература 10 класс", "file": "books/literatura10.pdf", "class": "10"},
    {"id": 13, "title": "Война и мир", "file": "books/war_and_peace.pdf", "class": "11"},
]

# Главная страница
@app.route('/')
def home():
    classes = sorted(set(book["class"] for book in books))
    return render_template('index.html', classes=classes)

# Получение списка книг с возможностью поиска
@app.route('/books', methods=['GET'])
def get_books():
    search_query = request.args.get('search', '').lower()
    filtered_books = [book for book in books if search_query in book['title'].lower()]
    return jsonify(filtered_books)

# Страница для книг конкретного класса
@app.route('/class/<class_number>')
def class_books(class_number):
    class_books_list = [book for book in books if book["class"] == class_number]
    if not class_books_list:
        return redirect('/not-found')  # Изменено: Убрано .html
    return render_template('class_books.html', class_number=class_number, books=class_books_list)

# Отображение книги
@app.route('/book/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if not book or not os.path.exists(book['file']):
        return redirect('/not-found')  # Изменено: Убрано .html

    doc = fitz.open(book['file'])
    total_pages = len(doc)  # Получаем общее количество страниц
    doc.close()
    return render_template('reader.html', book_id=book_id, book_title=book['title'], total_pages=total_pages)

# Получение страницы книги в виде изображения
@app.route('/book/<int:book_id>/pages/<int:page_num>', methods=['GET'])
def get_book_page(book_id, page_num):
    try:
        book = next((book for book in books if book['id'] == book_id), None)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        book_file = book['file']
        if not os.path.exists(book_file):
            return jsonify({"error": f"Book file not found: {book_file}"}), 404

        doc = fitz.open(book_file)
        if page_num < 0 or page_num >= len(doc):
            doc.close()
            return jsonify({"error": f"Page number out of range: {page_num}"}), 404

        page = doc[page_num]
        img = page.get_pixmap(dpi=100)  # Уменьшаем DPI для меньшего размера

        # Конвертируем изображение
        img_bytes = img.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        # Обрезаем белые/прозрачные поля
        image = image.crop(image.getbbox())

        # Сохраняем обрезанное изображение
        img_path = f"static/pages/book_{book_id}_page_{page_num}.png"
        if not os.path.exists(img_path):  # Проверяем, существует ли файл
            image.save(img_path, "PNG", optimize=True)

        doc.close()

        return jsonify({"image_url": f"/static/pages/book_{book_id}_page_{page_num}.png"})

    except Exception as e:
        print(f"Error in get_book_page (book_id={book_id}, page_num={page_num}): {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    except Exception as e:
        # Логируем ошибку для отладки
        print(f"Error in get_book_page: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Изменено: Убрано .html из маршрута
@app.route('/not-found')
def not_found():
    return render_template('not-found.html')

if __name__ == '__main__':
    os.makedirs("static/pages", exist_ok=True)  # Создаем папку для изображений страниц
    app.run(debug=True)