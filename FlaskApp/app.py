from flask import Flask
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, ValidationError
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://testuser:hallo123@127.0.0.1:3306/authors'
db = SQLAlchemy(app)

class Author(db.Model):
    __tablename__ = "author"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))
    specialisation = db.Column(db.String(50))

    def __init__(self, name, specialisation):
        self.name=name
        self.specialisation=specialisation

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

db.create_all()

class AuthorSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Author
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    specialisation = fields.String(required=True)


@app.route('/createAuthor', methods = ['POST'])
def create_author():
    try:
        data = request.get_json()
        author_schema = AuthorSchema()
        author = author_schema.load(data)
        if Author.query.filter_by(name=data.get("name")).first():
            return make_response(jsonify({'error': 'author does already exist.'}), 401)
        result = author_schema.dump(author.create())
        return make_response(jsonify({"author": result}),201)
    except ValidationError as e:
        return make_response(jsonify({'error': f'{e.messages}'}), 401)
    except Exception:
        return make_response(jsonify({'error': 'an unkown issue caused this error.'}), 500)

@app.route('/getAuthors', methods = ['GET'])
def get_authors():
    try:
        get_authors = Author.query.all()
        author_schema = AuthorSchema(many=True)
        authors = author_schema.dump(get_authors)
        return make_response(jsonify({"authors": authors}))
    except Exception:
        return make_response(jsonify({'error': 'an unkown issue caused this error.'}), 500)


@app.route('/updateAuthor/<int:id>', methods = ['PUT'])
def update_author_by_id(id):
    try:
        data = request.get_json()
        get_author = Author.query.get(id)
        if not get_author:
            return make_response(jsonify({'error': 'author does not exist.'}), 404)
        if data.get('specialisation'):
            get_author.specialisation = data['specialisation']
        if data.get('name'):
            get_author.name = data['name']
        db.session.add(get_author)
        db.session.commit()
        author_schema = AuthorSchema(only=['id', 'name','specialisation'])
        author = author_schema.dump(get_author)
        return make_response(jsonify({"author": author}))
    except Exception:
        return make_response(jsonify({'error': 'an unkown issue caused this error.'}), 500)      


@app.route('/deleteAuthor/<int:id>', methods = ['DELETE'])
def delete_author_by_id(id):
    try:
        get_author = Author.query.get(id)
        if not get_author:
            return make_response(jsonify({'error': 'author does not exist.'}), 404)
        db.session.delete(get_author)
        db.session.commit()
        return make_response("",204)
    except Exception:
        return make_response(jsonify({'error': 'an unkown issue caused this error.'}), 500)


if __name__ == "__main__":
 app.run(debug=True)
