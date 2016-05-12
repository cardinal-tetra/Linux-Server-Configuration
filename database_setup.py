from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    email = Column(String, nullable = False)
    picture = Column(String, nullable = False)

class Category(Base):
    __tablename__ = 'Category'
    name = Column(String, primary_key = True)

class Items(Base):
    __tablename__ = 'Items'
    name = Column(String, primary_key = True)
    image = Column(String, nullable = False)
    description = Column(String, nullable = False)
    user_id = Column(Integer, ForeignKey('Users.id'))
    cat_name = Column(String, ForeignKey('Category.name'))
    
    # we have added a decorator and serialize function as part of making a JSON endpoint
    @property
    def serialize(self):
        return {
            'creator_id' : self.user_id,
            'image' : self.image,
            'description' : self.description,
            'family' : self.cat_name,
            'name' : self.name,
        }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)