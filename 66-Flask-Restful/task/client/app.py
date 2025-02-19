from flask import Flask, render_template, redirect, url_for, request
import requests
import json
from forms import ItemForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfgsfdgsdfgsdfgsdf'


@app.route('/items')
def index():
    # Nusiųskite GET užklausą į savo API, kad gautumėte visus įrašus

    # Vietoje tuščio sąrašo padarykite, kad būtų sąrašas įrašų, gautų iš API
    items = []
    return render_template("items.html", items=items)


@app.route('/items/<id>')
def item(id):
    # Nusiųskite GET užklausą į savo API, kad gautumėte įrašą su atitinkamu ID

    # Vietoje tuščio žodyno padarykite, kad būtų žodynas, gautas iš API
    item = {}
    return render_template("item.html", item=item)


@app.route('/items/<id>/update', methods=['GET', 'POST'])
def update_item(id):
    # Nusiųskite GET užklausą į savo API, kad gautumėte įrašą su atitinkamu ID

    # Vietoje tuščio žodyno padarykite, kad būtų žodynas, gautas iš API
    item = {}
    form = ItemForm()
    if form.validate_on_submit():
        # Sukurti žodyną su informacija iš formos

        # Nusiųsti PUT užklausą į savo API, kad atnaujintumėte įrašą su informacija iš formos.
        return redirect(url_for('item', id=id))
    elif request.method == 'GET':
        form.title.data = item['title']
        form.price.data = item['price']
        form.quantity.data = item['quantity']
    return render_template("update_item.html", form=form)


@app.route('/delete/<id>')
def delete_item(id):
    # Nusiųsti DELETE užklausą į savo API, kad ištrintumėte įrašą
    return redirect(url_for('index'))


@app.route("/items/new", methods=["GET", "POST"])
def new_item():
    form = ItemForm()
    if form.validate_on_submit():
        # Sukurti žodyną su informacija iš formos

        # Nusiųsti POST užklausą į savo API, kad sukurtumėte naują įrašą su nauja informacija iš formos.
        return redirect(url_for('index'))
    return render_template("new_item.html", form=form)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
