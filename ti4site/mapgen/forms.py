from django import forms

class OptimizeForm(forms.Form):
    n_player_choices = [(n, str(n)) for n in [4, 5, 6]]
    n_players = forms.ChoiceField(choices=n_player_choices,
                                  label="Number of Players")
