from flask import Flask, render_template, redirect, request
from flask import make_response, jsonify
from data import db_session

from data.users import User
from data.games import Game
from data.comments import Comment
from data.photo import Photo
from data.notifications import Notification

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.login import LoginForm
from forms.user import RegisterForm
from forms.profile_edit import ProfileEditForm
from forms.add_game import AddGameForm
from forms.make_comment import MakeCommentForm

from werkzeug.utils import secure_filename
import os

from flask_restful import Api
from data import users_api
from data import games_api

# инициализация приложения и подключение API
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


# вызов ошибки 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# вызов ошибки 400
@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


# текущий пользователь
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


# главная страница
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect('/preview')

    db_sess = db_session.create_session()
    games = db_sess.query(Game).filter(Game.in_moderate == False).all()
    photos = [game.photo[0] for game in games]
    return render_template('moderation.html', title='GameStarter', games=games, photos=photos)


# предпросмотр для неавторизированных пользователей
@app.route('/preview')
def preview():
    return render_template('preview.html', title='Обзор') \
 \
        # пасхалка


@app.route('/shlack')
def shlack():
    return """<h1>Пайгейm для лохов</h1>
            <img src="https://i.ytimg.com/vi/GTLAPx5wX30/maxresdefault.jpg">
            <img src="https://i.ytimg.com/vi/YCYqpJp3JdU/maxresdefault.jpg">"""


# регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    # для неавторизованых пользователей
    if current_user.is_authenticated:
        redirect('/')
    form = RegisterForm()  # форма регистрации
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        # проверка на корректность введенных данных
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

        # новый пользователь
        user = User(
            name=f'{form.name.data} {form.surname.data}',
            email=form.email.data,
            nickname=form.nickname.data,
            favorites=''
        )

        # пароль
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        # самому первому пользователю даём модераторские права
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
        if user.id == 1:
            user.is_moderator = True

        # аватар
        f = form.profile_image.data
        if f:
            f.save(fr'static/profile_images/{user.id}{f.filename[-4:]}')
            user.profile_image = fr'/static/profile_images/{user.id}{f.filename[-4:]}'

        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


# переход в профиль
# если пользователь перещёл на свой аккаунт, то появляются кнопки выхода и редактирования аккаунта
@app.route('/profile/<nickname>')
def profile(nickname: str):
    if not current_user.is_authenticated:
        return redirect('/preview')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == nickname).first()  # пользовательь
    games = db_sess.query(Game).filter(Game.author == user.id)  # игры пользователя
    photos = [game.photo[0] for game in games]  # картинки игр
    return render_template('profile.html', title='Профиль', user=user, games=games, photos=photos)


# уведомления пользователя
@app.route('/notifications')
def notifications():
    if not current_user.is_authenticated:
        return redirect('/preview')
    notifications = current_user.notifications
    notifications.sort(key=lambda x: x.created_date)  # сортировака по дате
    return render_template('notifications.html', title='Уведомления', notifications=notifications)


# редактирование профиля
@app.route('/profile/edit', methods=['POST', 'GET'])
def profile_edit():
    if not current_user.is_authenticated:
        return redirect('/preview')
    form = ProfileEditForm()
    if request.method == "GET":  # запись данных в форму
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        form.name.data = user.name.split()[0]
        form.surname.data = user.name.split()[1]
        form.email.data = user.email
        form.nickname.data = user.nickname

    if form.validate_on_submit():  # изменение данных пользователя
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        # проверка на корректность введенных данных
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

        # изменение данных пользователя
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.name = f'{form.name.data} {form.surname.data}'
        user.email = form.email.data
        user.nickname = form.nickname.data
        db_sess.commit()
        return redirect(f'/profile/{form.nickname.data}')

    return render_template('edit_profile.html',
                           title='Редактирование профиля',
                           form=form)


# вход в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()  # форма авторизации
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


# выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# дообавление игры
@app.route('/game/add', methods=['GET', 'POST'])
def add_game():
    if not current_user.is_authenticated:
        return redirect('/preview')
    form = AddGameForm()  # форма добавления игры
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # проверка корректности введенных данных
        if db_sess.query(Game).filter(Game.name == form.name.data).first():
            return render_template('add_game.html', title='Добавление игры',
                                   form=form,
                                   message="Игра с таким названием уже существует")
        # создание новой игры в бд
        game = Game(
            name=form.name.data,
            description=form.description.data,
            author=current_user.id,
            in_moderate=1
        )

        db_sess.add(game)
        db_sess.commit()
        game = db_sess.query(Game).filter(Game.name.like(form.name.data)).first()

        # загрузка фотографий игры
        for number, file in enumerate(form.screenshots.data):
            filename = file.filename
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.png'):
                try:
                    os.mkdir(fr'static/games/{game.name}/')
                except Exception:
                    pass
                try:
                    os.mkdir(fr'static/games/{game.name}/screenshots/')
                except Exception:
                    pass

                file.save(fr'static/games/{game.name}/screenshots/{number + 1}.{filename[-3:]}')
                photo = Photo(path=fr'/static/games/{game.name}/screenshots/{number + 1}.{filename[-3:]}',
                              parent_game=game.id)
                game.photo.append(photo)
            else:
                return render_template('add_game.html', title='Добавление игры',
                                       form=form,
                                       message="Файл не является изображением")
        # сохранение фотографий
        game_files = form.game_files.data
        filename = game_files.filename
        file.save(fr'static/games/{game.name}/{game.name}.{filename[-3:]}')
        game.game_files = fr'/static/games/{game.name}/{game.name}.{filename[-3:]}'

        if form.github_link.data:
            if form.github_link.data.startswith("https://github.com/"):
                game.github_link = form.github_link.data
            else:
                return render_template('add_game.html', title='Добавление игры',
                                       form=form,
                                       message="Некорретная ссылка на github")
        db_sess.commit()
        return render_template('game_loaded.html', title='Игра добавлена')
    return render_template('add_game.html', title='Добавление игры', form=form)


# страница модерации
@app.route('/moderation')
def moderation():
    if not current_user.is_authenticated:
        return redirect('/preview')

    if not current_user.is_moderator:
        return render_template('not_permission.html', title='уходи')

    db_sess = db_session.create_session()
    games = db_sess.query(Game).filter(Game.in_moderate == True).all()
    photos = [game.photo[0] for game in games]
    return render_template('moderation.html', title='Модерация', games=games, photos=photos)


# страница игры
@app.route('/game/<game_name>', methods=['GET', 'POST'])
def game_page(game_name):
    if not current_user.is_authenticated:
        return redirect('/preview')
    db_sess = db_session.create_session()
    # игра и комментарии
    game = db_sess.query(Game).filter(Game.name.like(game_name)).first()
    make_comment_form = MakeCommentForm()
    comments = db_sess.query(Comment).filter(Comment.gameid == game.id)
    if game.in_moderate == 1 and not current_user.is_moderator:
        return render_template('not_permission.html', title='уходи')

    # cнова комментарии
    if make_comment_form.validate_on_submit():
        comment = Comment(
            text=make_comment_form.text.data,
            gameid=game.id,
            userid=current_user.id
        )
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/game/{game_name}')
    return render_template('game_page.html', title=game.name, game=game, photos=game.photo, author=game.user,
                           form=make_comment_form, comments=comments)


# удаление комментариев
@app.route('/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
    if not current_user.is_authenticated:
        return redirect('/preview')
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == comment_id).first()
    if comment.user.id != current_user.id and not current_user.is_moderator:
        return render_template('not_permission.html', title='уходи')
    game_name = comment.game.name
    db_sess.delete(comment)
    db_sess.commit()
    return redirect(f'/game/{game_name}')


# подтверждение публикации игры
@app.route('/public-game-access/<game_name>')
def access_public_game(game_name):
    if not current_user.is_authenticated:
        return redirect('/preview')
    return render_template('access.html', type='public', game_name=game_name)


# подтвержедение блокировки игры
@app.route('/block-game-access/<game_name>')
def access_block_game(game_name):
    if not current_user.is_authenticated:
        return redirect('/preview')
    return render_template('access.html', type='block', game_name=game_name)


# публикация игры
@app.route('/public-game/<game_name>')
def public_game(game_name):
    if not current_user.is_authenticated:
        return redirect('/preview')
    if not current_user.is_moderator:
        return render_template('not_permission.html', title='уходи')
    db_sess = db_session.create_session()
    game = db_sess.query(Game).filter(Game.name.like(game_name)).first()
    game.in_moderate = 0
    notification = Notification(
        game_name=game_name,
        for_user=game.author,
        status_nice=1
    )

    # уведомление о публикации
    game.user.notifications.append(notification)
    db_sess.commit()
    return render_template('public_game.html', title="Публикация")


# блокировка игры
@app.route('/block-game/<game_name>')
def block_game(game_name):
    if not current_user.is_authenticated:
        return redirect('/preview')
    if not current_user.is_moderator:
        return render_template('not_permission.html', title='уходи')
    db_sess = db_session.create_session()
    game = db_sess.query(Game).filter(Game.name.like(game_name)).first()
    db_sess.delete(game)
    notification = Notification(
        game_name=game_name,
        for_user=game.author,
        status_nice=0
    )
    # уведомление о блокировке
    game.user.notifications.append(notification)
    db_sess.commit()
    return render_template('block_game.html', title='Удаление игры')


# избранное
@app.route('/favourites')
def favorites():
    if not current_user.is_authenticated:
        return redirect('/preview')
    db_sess = db_session.create_session()
    favourites = current_user.favorites
    games = db_sess.query(Game).filter(Game.in_moderate == False).all()
    photos = [game.photo[0] for game in games]
    return render_template('favourites.html', title='Избранное', games=games, photos=photos)


# добавить игру в избранное
@app.route('/add_to_favourite/<game_name>')
def add_to_fovorite(game_name):
    if not current_user.is_authenticated:
        return redirect('/preview')
    db_sess = db_session.create_session()
    game = db_sess.query(Game).filter(Game.name.like(game_name)).first()
    if not game.name or game.in_moderate:
        return render_template('not_permission.html', title='уходи')
    game.user.favorites += str(game.id) + ' '
    db_sess.commit()
    return redirect(f'/game/{game_name}')


# удаление из избранного
@app.route('/delete_from_favourite/<game_name>')
def delete_from_favorite(game_name):
    if not current_user.is_authenticated:
        return redirect('/preview')
    db_sess = db_session.create_session()
    game = db_sess.query(Game).filter(Game.name.like(game_name)).first()
    if not game.name or game.in_moderate:
        return render_template('not_permission.html', title='уходи')
    game.user.favorites = game.user.favorites.replace(str(game.id) + ' ', '')
    db_sess.commit()
    return redirect(f'/game/{game_name}')


# поставить лайк комментарию(неопубликованная функция)
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


# поставить лайк игре(неопубликованная функция)
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


# запуск приложения
def main():
    db_session.global_init("db/games.sqlite")
    app.register_blueprint(games_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.run('127.0.0.1', port=800, debug=True)


if __name__ == '__main__':
    main()
