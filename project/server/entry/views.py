from flask import (
    request, redirect, url_for, render_template, flash, Blueprint
)

from project.server import db
from project.server.models import Entry


entry_blueprint = Blueprint("entry", __name__)


@entry_blueprint.route('/entries/')
def show_entries():
    entries = Entry.query.order_by(Entry.id.desc()).all()
    return render_template('entry/show_entries.html', entries=entries)


@entry_blueprint.route('/entries/add', methods=['POST'])
def add_entry():
    entry = Entry(
            title=request.form['title'],
            text=request.form['text']
            )
    db.session.add(entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('entry.show_entries'))
