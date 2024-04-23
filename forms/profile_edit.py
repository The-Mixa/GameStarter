from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


# изменение профиля
# почта, имя, фамилия, никнейм
class ProfileEditForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    nickname = StringField('Никнейм', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
