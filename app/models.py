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


# TABLE MODEL FOR API KEYS
class Keys(db.Model):
    __tablename__ = 'keys'
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String)


db.create_all()
