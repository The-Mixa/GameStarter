from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, FileField
from wtforms.validators import DataRequired


class AddGameForm(FlaskForm):
    name = StringField('Название игры', validators=[DataRequired()])
    description = StringField('Описание игры', validators=[DataRequired()])
    screenshots = FileField('Скриншоты', validators=[DataRequired()])