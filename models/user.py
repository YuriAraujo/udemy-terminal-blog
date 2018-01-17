import uuid

import datetime
from flask import session

from common.database import Database
from models.blog import Blog


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def search_email(cls, email):
        user_email = Database.find_one('users', {'email': email})
        if user_email is not None:
            return cls(**user_email)

    @classmethod
    def search_id(cls, _id):
        user_id = Database.find_one('users', {'id': _id}
                                    )
        if user_id is not None:
            return cls(**user_id)

    @staticmethod
    def validate_login(email, password):
        user =  User.search_email(email)
        if user is not None:
            return user.password == password
        return False

    @classmethod
    def register(cls, email, password):
        user = cls.search_email(email)
        if user is None:
            new_user = cls(email=email,
                            password=password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    @staticmethod
    def login(user_email):
        session['email'] = user_email

    @staticmethod
    def logou():
        session['email'] = None

    def get_blogs(self):
        return Blog.search_author_id(self._id)

    def new_blog(self, title, description):
        blog = Blog(author=self.email,
                    title=title,
                    description=description,
                    author_id=self._id)
        blog.save_to_mongo()

    @staticmethod
    def new_post(blog_id,title, content, date=datetime.datetime.utcnow()):
        blog = Blog.from_mongo(blog_id)
        blog.new_post(title=title,
                      content=content,
                      date=date)

    def json(self):
        return {
            "email": self.email,
            "_id": self._id,
            "password": self.password,

        }

    def save_to_mongo(self):
        Database.insert("users", self.json())