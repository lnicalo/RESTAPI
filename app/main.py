from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from collections import Counter
import requests

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@flask_mysql:3306/db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

if db is None:
    db.create_all()
    db.session.commit()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    github_name = db.Column(db.Text, nullable=True)
    github_following = db.Column(db.Integer)


@app.before_first_request
def create_tables():
    db.create_all()


class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'surname', 'lastname', 'github_name', 'github_following')
        model = Post


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


class PostsResource(Resource):
    def get(self):
        return posts_schema.dump(Post.query.all())

    def post(self):
        data = request.json
        post = Post(name=data['name'], surname=data['surname'], lastname=data['lastname'],
                    github_name=data['github_name'], github_following=data['github_following'])
        db.session.add(post)
        db.session.commit()
        return post_schema.dump(post)


class PostResource(Resource):
    def get(self, pk):
        return post_schema.dump(Post.query.get_or_404(pk))

    def patch(self, pk):
        data = request.json
        post = Post.query.get_or_404(pk)

        if 'name' in data:
            post.name = data['name']

        if 'surname' in data:
            post.surname = data['surname']

        if 'lastname' in data:
            post.lastname = data['lastname']

        if 'github_name' in data:
            post.github_name = data['github_name']

        if 'github_following' in data:
            post.github_following = data['github_following']

        db.session.commit()
        return post_schema.dump(post)

    def delete(self, pk):
        post = Post.query.get_or_404(pk)
        db.session.delete(post)
        db.session.commit()
        return '', 204


class FollowingResource(Resource):
    def get(self, pk):
        post = Post.query.get_or_404(pk)
        gn = post.github_name
        url = 'https://api.github.com/users/' + gn + '/following'
        data = requests.get(url=url).json()
        resul = Counter(post['login'] for post in data)
        entries = 0
        for k, v in resul.items():
            entries += v
        post.github_following = entries
        db.session.commit()
        return post_schema.dump(post)


api.add_resource(PostResource, '/post/<int:pk>')
api.add_resource(PostsResource, '/posts')
api.add_resource(FollowingResource, '/following/<int:pk>')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
