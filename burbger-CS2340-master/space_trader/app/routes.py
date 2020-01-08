from flask import redirect, url_for, request, jsonify
from flask_wtf import FlaskForm
from . import instance
from .forms import StartForm, IndexForm, GameForm, WinForm, LoseForm, ReturnForm
from .objects import Game, Player
from .request_handlers import request_types

@instance.route('/')
def null_page():
    return redirect(url_for('index'))


@instance.route('/index')
def index():
    index_form = IndexForm()
    return index_form.render()


@instance.route('/start', methods=['GET', 'POST'])
def start():
    start_form = StartForm()

    if start_form.validate_on_submit():
        player_info = [
            start_form.name.data,
            {'pilot': start_form.pilot_skill.data,
             'fighter': start_form.fighter_skill.data,
             'merchant': start_form.merchant_skill.data,
             'engineer': start_form.engineer_skill.data}
        ]
        instance.game = Game.new(player_info, int(start_form.difficulty.data))
        return redirect(url_for('game'))

    return start_form.render()


@instance.route('/game', methods=['GET'])
def game():
    player = Player()
    game_form = GameForm()
    game_form.title = player.name
    game_form.post_location.data = url_for('command')
    game_form.game_over_url.data = url_for('game_over')

    return game_form.render()

@instance.route('/command', methods=['POST'])
def command():
    form = FlaskForm()
    player = Player()
    if request.method == 'POST' and form.validate():
        request_type = request.form["type"]
        if request_type in request_types:
            print(f"Got command {request_type}")
            response = request_types[request_type](request.form)
            if player.won or player.lost:
                response['game_over'] = True
        else:
            print("No command - INNER")
            response = "No command sent", 422, {'Content-Type': 'text/plain'}
    elif request.method == 'POST':
        print("Validation failed")
        response = "Failed to validate", 403, {'Content-Type': 'text/plain'}
    else:
        print("No command - OUTER")
        response = "No command sent", 422, {'Content-Type': 'text/plain'}
    if player.won or player.lost:
        response['game_over'] = True
    response = jsonify(response)
    return response

@instance.route('/game_over', methods=['GET'])
def game_over():
    player = Player()
    if player.won:
        win_form = WinForm()
        win_form.title = f"Congratulations, {player.name}!"
        return win_form.render()
    elif player.lost:
        lose_form = LoseForm()
        return lose_form.render()
    else:
        return_form = ReturnForm()
        return return_form.render()
