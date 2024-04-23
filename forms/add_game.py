from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, TextAreaField, MultipleFileField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

# добавление новой игры
# имя, описение и различные файлы
class AddGameForm(FlaskForm):
    name = StringField('Название игры', validators=[DataRequired()])
    description = TextAreaField('Описание игры', validators=[DataRequired()])
    github_link = StringField('Ссылка на GitHub(не обязательно)')
    screenshots = MultipleFileField('Скриншоты', validators=[DataRequired(), FileAllowed(['jpg', 'png'], 'Только изображения!')])
    game_files = FileField('Архив с игрой', validators=[DataRequired(), FileAllowed(['zip', 'rar', '7z' ], 'Только архивы!')])
    submit = SubmitField('Добавить')