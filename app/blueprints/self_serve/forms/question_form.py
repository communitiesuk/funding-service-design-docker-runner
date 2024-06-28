from wtforms import RadioField
from wtforms import StringField, SubmitField
from wtforms.validators import Email
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm
from wtforms.widgets import RadioInput


class GovUkRadioField(RadioField):
    govuk_choices_format: list

    def __init__(self, *args, **kwargs):
        super(GovUkRadioField, self).__init__(*args, **kwargs)
        self.govuk_choices_format = [{"value": choice, "text": label} for choice, label in self.choices]


class QuestionForm(FlaskForm):

    id = StringField(
        label="Question ID",
        validators=[InputRequired(message="Supply a unique ID")],
    )
    title = StringField(label="Question text", validators=[InputRequired(message="Supply a question title")])
    hint = StringField(label="Hint text")
    question_type = GovUkRadioField(
        label="Question type",
        validators=[InputRequired(message="Select question type")],
        choices=[("TextField", "Short text"), ("FreeTextField", "Multi line text")],
        widget=RadioInput,
    )

    # list
    # conditions
    def as_dict(self):
        return {field_name: field.data for field_name, field in self._fields.items()}
