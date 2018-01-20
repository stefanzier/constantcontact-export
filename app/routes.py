from flask import render_template
from app import app
from app.forms import RetrieveCSVForm
from app.models.export import download_csv


@app.route('/')
@app.route('/index', methods=["GET", "POST"])
def index():
    form = RetrieveCSVForm()
    if form.validate_on_submit():
        return download_csv(form.eventId.data)

    return render_template('index.html', form=form)


@app.errorhandler(500)
def pageNotFound(error):
    return "Uh oh! Please go back and check your Event ID"
