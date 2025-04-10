import os
import fitz  # PyMuPDF
from PIL import Image
import io

# Список книг (копируем из app.py)
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

def generate_page(book_id, book_file, page_num):
    """
    Генерирует изображение для указанной страницы книги и сохраняет его в static/pages/.
    """
    try:
        # Проверяем, существует ли PDF-файл
        if not os.path.exists(book_file):
            print(f"Ошибка: Файл {book_file} не найден")
            return False

        # Открываем PDF
        doc = fitz.open(book_file)
        if page_num < 0 or page_num >= len(doc):
            print(f"Ошибка: Номер страницы {page_num} вне диапазона для книги {book_file}")
            doc.close()
            return False

        # Путь для сохранения изображения
        img_path = f"static/pages/book_{book_id}_page_{page_num}.jpg"  # Используем JPG для меньшего размера

        # Проверяем, существует ли уже файл
        if os.path.exists(img_path):
            print(f"Страница {page_num} для книги {book_id} уже сгенерирована: {img_path}")
            doc.close()
            return True

        # Генерируем изображение страницы
        page = doc[page_num]
        img = page.get_pixmap(dpi=100)  # Уменьшаем DPI для меньшего размера

        # Конвертируем изображение в формат, который можно обработать с помощью Pillow
        img_bytes = img.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        # Обрезаем белые/прозрачные поля
        image = image.crop(image.getbbox())

        # Сохраняем изображение
        image.save(img_path, "JPEG", quality=80, optimize=True)
        print(f"Сгенерирована страница {page_num} для книги {book_id}: {img_path}")

        doc.close()
        return True

    except Exception as e:
        print(f"Ошибка при генерации страницы {page_num} для книги {book_id}: {str(e)}")
        return False

def generate_all_pages():
    """
    Проходит по всем книгам и генерирует изображения для всех страниц.
    """
    # Создаем папку static/pages/, если она не существует
    os.makedirs("static/pages", exist_ok=True)

    # Проходим по всем книгам
    for book in books:
        book_id = book['id']
        book_file = book['file']
        book_title = book['title']

        print(f"\nОбработка книги: {book_title} (ID: {book_id})")

        # Проверяем, существует ли PDF-файл
        if not os.path.exists(book_file):
            print(f"Файл {book_file} не найден, пропускаем книгу")
            continue

        # Открываем PDF, чтобы узнать общее количество страниц
        try:
            doc = fitz.open(book_file)
            total_pages = len(doc)
            doc.close()
        except Exception as e:
            print(f"Ошибка при открытии PDF {book_file}: {str(e)}")
            continue

        print(f"Всего страниц: {total_pages}")

        # Генерируем изображения для всех страниц
        for page_num in range(total_pages):
            success = generate_page(book_id, book_file, page_num)
            if not success:
                print(f"Пропускаем страницу {page_num} из-за ошибки")

if __name__ == '__main__':
    print("Запуск генерации страниц для всех учебников...")
    generate_all_pages()
    print("Генерация завершена!")