from flask import Blueprint, request, jsonify
from models import db, Book, Student, Borrow
from datetime import datetime

books_bp = Blueprint('books', __name__)

#  Récupérer tous les livres
@books_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([
        {
            'id': b.id, 
            'title': b.title, 
            'author': b.author, 
            'published_at': b.published_at.strftime('%Y-%m-%d') if b.published_at else None,
            'is_borrowed': b.is_borrowed,
            'current_borrower': b.current_borrower
        }
        for b in books
    ])

#  Récup livre par id
@books_bp.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'published_at': book.published_at.strftime('%Y-%m-%d') if book.published_at else None,
        'is_borrowed': book.is_borrowed,
        'current_borrower': book.current_borrower
    })

#  Ajouter livre
@books_bp.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()

    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'Invalid data, title and author are required'}), 400

    published_at = None
    if 'published_at' in data:
        try:
            published_at = datetime.strptime(data['published_at'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400

    book = Book(title=data['title'], author=data['author'], published_at=published_at)
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully', 'id': book.id}), 201

#  Maj un livre
@books_bp.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'published_at' in data:
        try:
            book.published_at = datetime.strptime(data['published_at'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400

    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

#  Supprimer livre
@books_bp.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

#  Emprunter livre
@books_bp.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    data = request.get_json()
    if not data or 'student_id' not in data:
        return jsonify({'error': 'Student ID is required'}), 400
    
    student_id = data['student_id']
    
    # Vérifier livre existe
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Vérifier étudiant existe
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Vérifier si livre déjà emprunté
    if book.is_borrowed:
        return jsonify({'error': 'Book is already borrowed'}), 400
    
    # Créer nouvel emprunt
    borrow = Borrow(book_id=book_id, student_id=student_id)
    db.session.add(borrow)
    db.session.commit()
    
    return jsonify({
        'message': 'Book borrowed successfully',
        'borrow_id': borrow.id,
        'borrowed_at': borrow.borrowed_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 201

#  Rendre livre
@books_bp.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    # Vérif livre existe
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Vérifier si livre déjà emprunté
    if not book.is_borrowed:
        return jsonify({'error': 'Book is not currently borrowed'}), 400
    
    # Trouver emprunt en cours
    borrow = Borrow.query.filter_by(book_id=book_id, returned_at=None).first()
    if not borrow:
        return jsonify({'error': 'Active borrow record not found'}), 500
    
    # Maj date de retour
    borrow.returned_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Book returned successfully',
        'borrow_id': borrow.id,
        'borrowed_at': borrow.borrowed_at.strftime('%Y-%m-%d %H:%M:%S'),
        'returned_at': borrow.returned_at.strftime('%Y-%m-%d %H:%M:%S')
    })

# Obtenir historique des emprunts d'un livre
@books_bp.route('/books/<int:book_id>/borrows', methods=['GET'])
def get_book_borrows(book_id):
    # Vérifier que le livre existe
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    borrows = Borrow.query.filter_by(book_id=book_id).all()
    return jsonify([
        {
            'id': b.id,
            'student_id': b.student_id,
            'student_name': f"{b.student.first_name} {b.student.last_name}",
            'borrowed_at': b.borrowed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'returned_at': b.returned_at.strftime('%Y-%m-%d %H:%M:%S') if b.returned_at else None
        }
        for b in borrows
    ])