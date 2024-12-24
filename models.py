import os
from sqlalchemy import Column, String, create_engine, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()




class User(Base):
    """"""

    __tablename__ = 'users'


    username = Column(String(20), primary_key=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)

    feedback = relationship('Feedback', back_populates='user', cascade='all, delete')


    def __init__(self, username, password, email, first_name, last_name):
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}',fist_name='{self.first_name}', last_name='{self.last_name}')>"
    

class Feedback(Base):

    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(String, nullable=False)
    username = Column(String, ForeignKey('users.username'), nullable=False)

    user = relationship('User', back_populates='feedback')

    def __repr__(self):
        return f"<Feedback(title='{self.title}', username='{self.username}')"

db_path = os.path.expanduser("~/users.db")
engine = create_engine(f'sqlite:///{db_path}', echo=True)
print(Base.metadata.tables)
