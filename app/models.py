from app import db


# TABLE MODEL FOR PRODUCTS
class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    offers = db.relationship('Offers', back_populates="product")

    def to_dict(self):
        products_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return products_dict


# TABLE MODEL FOR OFFERS
class Offers(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    items_in_stock = db.Column(db.Integer)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Products', back_populates="offers")

    def to_dict(self):
        products_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return products_dict


# TABLE MODEL FOR USERS
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(60), unique=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

    def to_dict(self):
        products_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns
                         if column.name != 'id'}
        return products_dict


db.create_all()
