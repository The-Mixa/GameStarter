from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# комментарий
# текст комментария
class MakeCommentForm(FlaskForm):
    text = StringField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')