"""Personal Library Management System:
Skills: OOP, file handling, JSON.
Description: Develop a system to manage a personal library. 
Users can add books, mark them as read/unread, 
and store book information in a JSON file."""
import json
import csv
import requests
import os
import fitz
import pytesseract
from PIL import Image
import docx
import re
import validators  # Import validators module for URL validation

class Book:
    def __init__(self):
        self.books_store = []
        self.filename = "books.json"
        self.books_directory = "books"
        os.makedirs(self.books_directory, exist_ok=True)
        self.load_books()

    def load_books(self):
        try:
            with open(self.filename, 'r') as b:
                try:
                    self.books_store = json.load(b)
                    print("Books loaded successfully!")
                except json.JSONDecodeError:
                    print("Starting with an empty book store.\n")
                    self.books_store = []
        except FileNotFoundError:
            print("Starting with an empty book store.\n")
            self.books_store = []

    def add_books(self):
        title = input("Enter book title: ")
        author = input("Enter the author of the book: ")
        publication_date = input("Enter the publication date: ")
        book_url = input("Enter the URL of the book: ")

        # Validate URL
        if not validators.url(book_url):
            print("Invalid URL. Please enter a valid URL.")
            return

        # Download book from URL
        response = requests.get(book_url)
        if response.status_code == 200:
            file_name = os.path.join(self.books_directory, os.path.basename(book_url))
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"Book downloaded and saved as '{file_name}'")
        else:
            print("Failed to download the book.")
            return

        new_book = {
            "title": title,
            "author": author,
            "year": publication_date,
            "file_path": file_name
        }
        self.books_store.append(new_book)
        print(f"You have successfully added '{new_book['title']}' to your Library")

    def read_book(self):
        title = input("Enter book title: ")
        for book in self.books_store:
            if book["title"] == title:
                file_path = book["file_path"]
                try:
                    if file_path.endswith('.pdf'):
                        with fitz.open(file_path) as pdf_file:
                            num_pages = pdf_file.page_count
                            print(f"Reading {title}: {num_pages} pages available.\n")
                            extracted_text = ""

                            for page_num in range(num_pages):
                                page = pdf_file[page_num]
                                text = page.get_text()
                                if not text.strip():
                                    pix = page.get_pixmap()
                                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                    text = pytesseract.image_to_string(img)
                                extracted_text += text

                            print(extracted_text)

                            with open(f"{title}.txt", 'w', encoding='utf-8') as txt_file:
                                txt_file.write(extracted_text)

                    elif file_path.endswith('.docx'):
                        doc = docx.Document(file_path)
                        extracted_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                        print(extracted_text)

                        with open(f"{title}.txt", 'w', encoding='utf-8') as txt_file:
                            txt_file.write(extracted_text)

                    else:
                        print(f"Unsupported file format for '{title}'.")

                except FileNotFoundError:
                    print(f"Book file '{file_path}' not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")

                return

        print(f"Book titled '{title}' not found in the store.")

    def edit_book(self):
        edit = input("Book title to edit: ")
        for book in self.books_store:
            if edit == book["title"]:
                new_title = input(f"Enter new title (current: '{book['title']}'): ").strip() or book['title']
                new_author = input(f"Enter new author (current: '{book['author']}'): ").strip() or book['author']
                new_publication_date = input(f"Enter new publication date (current: '{book['year']}'): ").strip() or book['year']
                new_file_path = input(f"Enter new file path (current: '{book['file_path']}'): ").strip() or book['file_path']

                if new_title != book['title']:
                    book["title"] = new_title
                if new_author != book['author']:
                    book["author"] = new_author
                if new_publication_date != book['year']:
                    book["year"] = new_publication_date
                if new_file_path != book['file_path']:
                    book["file_path"] = new_file_path

                print("Book details updated successfully!")
                return

        print("Book title not found.")

    def view_books(self):
        if not self.books_store:
            print("No books recorded.\n")
            return

        for i, book in enumerate(self.books_store, start=1):
            print(f"{i}. Title: {book['title']}\n Author: {book['author']}\n Publication Date: {book['year']}\n File Path: {book['file_path']} \n")

    def save_books(self):
        with open(self.filename, 'w') as b:
            json.dump(self.books_store, b, indent=4)
        print("Books saved successfully!")

    def remove_book(self):
        remove_book = input("Book title to delete: ")
        for i, book in enumerate(self.books_store):
            if remove_book == book["title"]:
                del self.books_store[i]
                print(f"Book '{remove_book}' deleted successfully!")
                return

        print(f"Book with title '{remove_book}' not found.")

    def export_as_csv(self, csv_filename='books.csv'):
        with open(self.filename, 'r') as json_file:
            books_store = json.load(json_file)

        with open(csv_filename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['title', 'author', 'year', 'file_path'])
            writer.writeheader()
            for book in books_store:
                writer.writerow({field: book[field] for field in writer.fieldnames})

        print("Books exported to CSV file successfully!")

def main():
    library = Book()

    while True:
        print("Library Management System")
        print("*************************")
        print("1. Add a Book")
        print("2. Edit Book")
        print("3. View Books")
        print("4. Delete Book")
        print("5. Save Books")
        print("6. Export to CSV")
        print("7. Read Book")
        print("8. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            library.add_books()
        elif choice == "2":
            library.edit_book()
        elif choice == "3":
            library.view_books()
        elif choice == "4":
            library.remove_book()
        elif choice == "5":
            library.save_books()
        elif choice == "6":
            library.export_as_csv()
        elif choice == "7":
            library.read_book()
        elif choice == "8":
            library.save_books()
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please choose a valid option.\n")

if __name__ == "__main__":
    main()
