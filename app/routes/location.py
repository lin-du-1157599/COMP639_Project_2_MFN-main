from flask import render_template, request

from app import app

@app.route('/map')
def show_map():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    name = request.args.get('name')
    return render_template('map.html', lat=lat, lng=lng, name=name)

