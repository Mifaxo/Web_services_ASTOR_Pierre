from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    published_at = db.Column(db.Date, nullable=True)
    
    # Relation avec les emprunts
    borrows = db.relationship('Borrow', backref='book', lazy=True)
    
    @property
    def is_borrowed(self):
        # Vérifie si le livre est actuellement emprunté
        for borrow in self.borrows:
            if borrow.returned_at is None:
                return True
        return False
    
    @property
    def current_borrower(self):
        # Retourne l'ID de l'étudiant qui a emprunté le livre
        for borrow in self.borrows:
            if borrow.returned_at is None:
                return borrow.student_id
        return None

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    
    # Relation avec les emprunts
    borrows = db.relationship('Borrow', backref='student', lazy=True)
    
    @property
    def borrowed_books(self):
        # Retourne les IDs des livres actuellement empruntés par l'étudiant
        return [borrow.book_id for borrow in self.borrows if borrow.returned_at is None]

class Borrow(db.Model):
    __tablename__ = 'borrows'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    borrowed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    returned_at = db.Column(db.DateTime, nullable=True)