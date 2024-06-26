from flask import Blueprint, request, jsonify
from models import db, Post, Comment, Users, Likes

api = Blueprint('api', __name__)

@api.route('/posts', methods=['POST'])
def create_post():
    data = request.json
    new_post = Post(
        image=data['image'],
        likes=data['likes'],
        nickname=data['nickname'],
        email=data['email'],
        description=data['description'],
        media_type=data['media_type']
    )
    db.session.add(new_post)
    db.session.commit()

    for comment in data.get('comments', []):
        new_comment = Comment(
            nickname=comment['nickname'],
            comment=comment['comment'],
            post_id=new_post.id
        )
        db.session.add(new_comment)

    for likeduser in data.get('liked_by', []):
        new_like_user = Likes(
            nickname=likeduser['nickname'],
            post_id=new_post.id
        )
        db.session.add(new_like_user)
    
    db.session.commit()
    return jsonify({'message': 'Post created successfully!'}), 201

@api.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    output = []

    for post in posts:
        post_data = {
            'id': post.id,
            'image': post.image,
            'likes': post.likes,
            'nickname': post.nickname,
            'email': post.email,
            'media_type': post.media_type,
            'description': post.description,
            'comments': [{'nickname': comment.nickname, 'comment': comment.comment} for comment in post.comments],
            'liked_by': [{'nickname': liked_by.nickname, 'post_id': liked_by.post_id} for liked_by in post.liked_by]
        }
        output.append(post_data)

    return jsonify({'posts': output})

@api.route('/posts/getpost/<int:post_id>', methods=['GET'])
def get_post(post_id):
    posts = Post.query.all()
    output = []

    for post in posts:
        post_data = {
            'id': post.id,
            'image': post.image,
            'likes': post.likes,
            'nickname': post.nickname,
            'email': post.email,
            'media_type': post.media_type,
            'description': post.description,
            'comments': [{'nickname': comment.nickname, 'comment': comment.comment} for comment in post.comments]
        }
        output.append(post_data)

    return jsonify({'posts': output[post_id - 1]})

@api.route('/users', methods=['GET'])
def get_users():
    users = Users.query.all()
    output = []

    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'password': user.password,
            'profile_image': user.profile_image
        }
        output.append(user_data)

    return jsonify({'users': output})

@api.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = Users(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        profile_image=data['profile_image'],
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully!'}), 201

@api.route('/users/getposts/<string:nickname>', methods=['GET'])
def search_user_posts(nickname):
    posts = Post.query.all()
    output = []

    for post in posts:
        if nickname == post.nickname:
            post_data = {
                'id': post.id,
                'image': post.image,
                'likes': post.likes,
                'nickname': post.nickname,
                'email': post.email,
                'media_type': post.media_type,
                'description': post.description,
                'comments': [{'nickname': comment.nickname, 'comment': comment.comment} for comment in post.comments]
            }
            output.append(post_data)

    return jsonify({'posts': output})

@api.route('/posts/patchpost/<int:post_id>', methods=['PATCH'])
def patch_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    comments_data = data.get('comments', [])
    
    Comment.query.filter_by(post_id=post.id).delete()

    for comment_data in comments_data:
        new_comment = Comment(
            nickname=comment_data.get('nickname'),
            comment=comment_data.get('comment'),
            post_id=post.id
        )
        db.session.add(new_comment)
    
    db.session.commit()
    return jsonify({'message': 'Post updated successfully'})

@api.route('/update_profile_image/<int:user_id>', methods=['PATCH'])
def update_profile_image(user_id):
    data = request.get_json()
    new_profile_image = data.get('profile_image')
    
    user = Users.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    if new_profile_image:
        user.profile_image = new_profile_image
        db.session.commit()
        return jsonify({"message": "Profile image updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid data"}), 400

@api.route('/posts/likeaction/<int:post_id>/<string:action>', methods=['PATCH'])
def like_post(post_id, action):
    post = Post.query.get_or_404(post_id)
    data = request.json
    if action == "like":
        post.likes += 1
        new_user_liked = Likes(
            nickname=data['nickname'],
            post_id=data['post_id']
        )
        db.session.add(new_user_liked)
        db.session.commit()
    elif action == "deslike":
        post.likes -= 1
        Likes.query.filter_by(nickname=data['nickname']).delete()
        db.session.commit()
    
    liked_users = Likes.query.filter_by(post_id=post_id).all()
    liked_usernames = [user.nickname for user in liked_users]


    return jsonify({"action": f"{action}", "liked_users": liked_usernames})

@api.route('/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    # Consulta para obter todos os comentários de um determinado post
    comments = Comment.query.filter_by(post_id=post_id).all()
    
    # Converta os comentários para uma lista de dicionários
    comments_list = [
        {
            'id': comment.id,
            'nickname': comment.nickname,
            'comment': comment.comment,
            'post_id': comment.post_id
        }
        for comment in comments
    ]
    
    return jsonify(comments_list)