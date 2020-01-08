from flask import render_template, url_for
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import (StringField, RadioField, IntegerField, SubmitField, ValidationError,
                     HiddenField)
from ordered_set import OrderedSet
from app.objects import Game, Universe, Player
from app import instance


def skill_check(form, field):
    if field.data < 0:
        raise ValidationError("Can't allocate negative skill points")

    form.allocated_skill_points += field.data

    if form.allocated_skill_points > form.max_skill_points:
        raise ValidationError(
            "Can't allocate more than {} skill points on the {} difficulty"
            .format(form.max_skill_points,
                    form.difficulty_setting)
        )


# superclass for all new forms we'll make - abstracts away a little bit of code
class SpaceTraderForm(FlaskForm):
    title = None
    template_file = 'index.html'

    def render(self, **kwargs):
        return render_template(
            self.template_file,
            instance=instance,
            game=Game(),
            universe=Universe(),
            player=Player(),
            form=self,
            **kwargs
        )

    def make_pylint_happy(self, arg):
        return self.__dict__[arg]


class StartForm(SpaceTraderForm):
    title = 'Start Game'
    template_file = 'start.html'
    allocated_skill_points = 0
    max_skill_points = 8
    difficulty_setting = 'Medium'
    error_message_set = OrderedSet()

    name = StringField('Name', validators=[DataRequired("Must input a name")])
    difficulty = RadioField('Difficulty', default='1', choices=[
        ('0', 'Easy'),
        ('1', 'Medium'),
        ('2', 'Hard')])
    pilot_skill = IntegerField(
        'Pilot Skill',
        validators=[DataRequired("Must input a pilot skill level"), skill_check]
    )
    fighter_skill = IntegerField(
        'Fighter Skill',
        validators=[DataRequired("Must input a fighter skill level"), skill_check]
    )
    merchant_skill = IntegerField(
        'Merchant Skill',
        validators=[DataRequired("Must input a merchant skill level"), skill_check]
    )
    engineer_skill = IntegerField(
        'Engineer Skill',
        validators=[DataRequired("Must input an engineer skill level"), skill_check]
    )
    done = SubmitField('Start New Game')

    def validate(self):
        self.difficulty_setting = self.difficulty.choices[int(self.difficulty.data)][1]
        self.max_skill_points = 16 - (4 * int(self.difficulty.data))
        super_return = super().validate()
        self.error_message_set = OrderedSet()
        for error in self.errors:
            self.error_message_set.add(self.errors[error][0])

        return super_return


class IndexForm(SpaceTraderForm):
    start_game = SubmitField('Start Game')


class GameForm(SpaceTraderForm):
    template_file = 'game.html'
    post_location = HiddenField()
    game_over_url = HiddenField()

class WinForm(SpaceTraderForm):
    player = Player()
    template_file = 'win.html'
    new_game = SubmitField('New Game')

class LoseForm(SpaceTraderForm):
    title = "Game Over"
    template_file = 'lose.html'
    new_game = SubmitField('New Game')

class ReturnForm(SpaceTraderForm):
    template_file = 'return.html'
    new_game = SubmitField('New Game')
    continue_game = SubmitField('Continue')
