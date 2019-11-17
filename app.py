from flask import Flask, request, Response, render_template, jsonify
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Regexp, ValidationError
import re

class WordForm(FlaskForm):
    avail_letters = StringField("Letters", validators= [Regexp(r'^[a-z]*$', message="must contain letters only")])
    pattern_match = StringField("Pattern", validators= [Regexp(r'^([a-z]|\.)*$', message="must contain letters and . only")])
    word_length = SelectField(u'Length', choices=[ ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('all', 'all')])
    submit = SubmitField("Submit")


csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/')
def index():
    form = WordForm()
    return render_template("index.html", form=form)


@app.route('/words', methods=['POST','GET'])
def letters_2_words():
    form = WordForm()
    if form.validate_on_submit():
        letters = form.avail_letters.data
        pattern = form.pattern_match.data
        length = form.word_length.data
    else:
        return render_template("index.html", form=form)

    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())
    word_set = set()
    error = ""
    if letters == '' and pattern == '':
        return render_template("index.html", form=form, error_msg="If no letters are given, please provide a pattern.")
    elif letters == '' and pattern != '':
        if length != 'all':
            if len(pattern) == int(length):
                pattern_set = set()
                for p in good_words:
                    if re.search('^' + pattern + '$', p):
                        pattern_set.add(p)
                for w in pattern_set:
                    word_set.add(w)
            elif len(pattern) != int(length):
                return render_template("index.html", form=form, error_msg="Length of pattern must match length specified.")
        else:
            pattern_set = set()
            for p in good_words:
                if re.search('^' + pattern + '$', p):
                    pattern_set.add(p)
            for w in pattern_set:
                    word_set.add(w)
    elif letters != '' and pattern == '':
        letters_set = set()
        for l in range(3,len(letters)+1):
            for word in itertools.permutations(letters,l):
                w = "".join(word)
                if w in good_words:
                    letters_set.add(w)
        if length != 'all':
            length_set = set()
            for x in letters_set:
                if len(x) == int(length):
                    length_set.add(x)
            for w in length_set:
                    word_set.add(w)
        else:
            for w in letters_set:
                word_set.add(w)
    elif letters != '' and pattern != '':
        letters_set = set()
        for l in range(3,len(letters)+1):
            for word in itertools.permutations(letters,l):
                w = "".join(word)
                if w in good_words:
                    letters_set.add(w)
                    if length != 'all':
                        if len(pattern) == int(length):
                            pattern_set = set()
                            for p in letters_set:
                                if re.search('^' + pattern + '$', p):
                                    pattern_set.add(p)
                                    for w in pattern_set:
                                        word_set.add(w)
    elif len(pattern) != int(length):
            return render_template("index.html", form=form, error_msg="Length of pattern must match length specified.")
    else:
        pattern_set = set()
        for p in letters_set:
            if re.search('^' + pattern + '$', p):
                pattern_set.add(p)
        for w in pattern_set:
                word_set.add(w)
    return render_template('wordlist.html',
        wordlist=sorted(sorted(word_set), key=len))  # first sort by length, then sort alphabetically

@app.route('/dict/<word>', methods=['GET'])
def dictproxy(word):
    x = requests.get(f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=bd559492-71c7-4e9a-9bdf-3950d664cf96')
    return jsonify(x.json())

@app.route('/proxy')
def proxy():
    x = requests.get(request.args['url'])
    resp = Response(x.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp


if __name__ == '__main__':
    app.run()
