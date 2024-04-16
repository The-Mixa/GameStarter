from flask import Flask, render_template, redirect, request
from flask import make_response, jsonify
from data import db_session

from data.users import User
from data.games import Game
from data.comments import Comment

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.login import LoginForm
from forms.user import RegisterForm
from forms.profile_edit import ProfileEditForm
from forms.add_game import AddGameForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect('/preview')
    return render_template('index.html', title='GameStarter')
        

@app.route('/preview')
def preview():
    return render_template('preview.html', title='Обзор')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть, выберите другую почту")

        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким никнеймом уже есть")
        

        user = User(
            name=f'{form.name.data} {form.surname.data}',
            email=form.email.data,
            nickname=form.nickname.data
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()

        # if 'file' in request.files:
        #     f = request.files['file']
        #     if f.filename.endswith('.jpg') or f.filename.endswith('.png'):
        #         file = open(f'static/profile_images/{user.id}.{f.filename[-3:]}', 'a')
        #         file.close()
        #         f.save(f'static/profile_images/{user.id}.{f.filename[-3:]}')
        #         user.profile_image = f'/static/profile_images/{user.id}.{f.filename[-3:]}'
        #     else:
        #         return render_template('register.html', title='Регистрация',
        #                                form=form,
        #                                message="Файл не является изображением")
        # else:
        #     user.profile_image = '/static/profile_images/default.png'

        f = form.profile_image.data
        print(f)
        f.save(fr'static/profile_images/{user.id}{f.filename[-4:]}')
        user.profile_image = fr'/static/profile_images/{user.id}{f.filename[-4:]}'

        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/profile/<nickname>')
def profile(nickname: str):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == nickname).first()
    return render_template('profile.html', title='Профиль', user=user)


@app.route('/profile/edit', methods=['POST', 'GET'])
def profile_edit():
    form = ProfileEditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        form.name.data = user.name.split()[0]
        form.surname.data = user.name.split()[1]
        form.email.data = user.email
        form.nickname.data = user.nickname

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if form.email.data != user.email:
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('edit_profile.html', title='Редактирование профиля',
                                    form=form,
                                    message="Такой пользователь уже есть, выберите другую почту")
        if form.nickname.data != user.nickname:
            if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
                return render_template('edit_profile.html', title='Редактирование профиля',
                                    form=form,
                                    message="Пользователь с таким никнеймом уже есть")
        
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.name = f'{form.name.data} {form.surname.data}'
        user.email = form.email.data
        user.nickname = form.nickname.data
        db_sess.commit()
        return redirect(f'/profile/{form.nickname.data}')

    return render_template('edit_profile.html',
                           title='Редактирование профиля',
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            (User.email == form.email_or_nickname.data) | (User.nickname == form.email_or_nickname.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/game/add', methods=['GET', 'POST'])
def add_game():
    form = AddGameForm()
    if form.validate_on_submit():   
        db_sess = db_session.create_session()
        if db_sess.query(Game).filter(Game.name == form.name.data).first():
            return render_template('add_game.html', title='Добавление игры',
                                   form=form,
                                   message="Игра с таким названием уже существует")
        game = Game(
            name=form.name.data,
            description=form.description.data,
            author = current_user.id,
            status = 0
        )
        if form.github_link.data:
            if form.github_link.data.startswith("https://github.com/"):
                game.github_link = form.github_link.data
            else:
                return render_template('add_game.html', title='Добавление игры',
                                       form=form,
                                       message="Некорретная ссылка на github")
        db_sess.add(game)
        db_sess.commit() 
        return render_template('game_loaded.html', title='Игра добавлена')
    return render_template('add_game.html', title='Добавление игры', form=form)


def make_reaction_to_comment(comment_id: int, user_id: int, type: str) -> None:
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == comment_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if type == 'like':
        user.comment_likes.append(comment)
        comment.likes += 1
    elif type == 'dislike':
        user.comment_dislikes.append(comment)
        comment.dislikes += 1


def make_reaction_to_game(game_id: int, user_id: int, type: str) -> None:
    db_sess = db_session.create_session()
    game = db_sess.query(Game).filter(Game.id == game_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if type == 'like':
        user.comment_likes.append(game)
        game.likes += 1
    elif type == 'dislike':
        user.comment_dislikes.append(game)
        game.dislikes += 1


def main():
    db_session.global_init("db/games.sqlite")
    app.run('127.0.0.1', port=800, debug=True)


if __name__ == '__main__':
    main()
 