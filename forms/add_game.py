from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class AddGameForm(FlaskForm):
    name = StringField('Название игры', validators=[DataRequired()])
    description = TextAreaField('Описание игры', validators=[DataRequired()])
    github_link = StringField('Ссылка на GitHub(не обязательно)')
    screenshots = MultipleFileField('Скриншоты', validators=[DataRequired(), FileAllowed(['jpg', 'png'], 'Только изображения!')])
    submit = SubmitField('Добавить')