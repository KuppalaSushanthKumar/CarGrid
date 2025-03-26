from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from models import db, Car

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/images'

db.init_app(app)

# Home/Search Page
@app.route('/')
@app.route('/search')
def search():
    cars = Car.query.all()
    grouped_cars = {}
    for car in cars:
        if car.company not in grouped_cars:
            grouped_cars[car.company] = []
        grouped_cars[car.company].append(car)
    return render_template('search.html', grouped_cars=grouped_cars)

# Search Results
@app.route('/search_results', methods=['GET'])
def search_results():
    company = request.args.get('company')
    price_range = request.args.get('price_range')
    car_type = request.args.get('car_type')
    fuel_type = request.args.get('fuel_type')

    query = Car.query
    if company:
        query = query.filter(Car.company.ilike(f"%{company}%"))
    if price_range:
        price_min, price_max = map(float, price_range.split('-'))
        query = query.filter(Car.price.between(price_min, price_max))
    if car_type and car_type != 'all':
        query = query.filter(Car.car_type == car_type)
    if fuel_type and fuel_type != 'all':
        query = query.filter(Car.fuel_type == fuel_type)

    cars = query.all()
    return render_template('search_results.html', cars=cars)

# Upload/Edit Car
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        car_id = request.form.get('car_id')
        car_name = request.form['car_name']
        company = request.form['company']
        model_year = request.form['model_year']
        car_type = request.form['car_type']
        fuel_type = request.form['fuel_type']
        price = request.form['price']

        if car_id:
            car = Car.query.get(car_id)
        else:
            car = Car()

        car.car_name = car_name
        car.company = company
        car.model_year = model_year
        car.car_type = car_type
        car.fuel_type = fuel_type
        car.price = price

        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                car.image = f"images/{filename}"

        if car_id:
            flash('Car updated successfully!', 'success')
        else:
            db.session.add(car)
            flash('Car uploaded successfully!', 'success')

        db.session.commit()
        return redirect(url_for('upload'))

    cars = Car.query.all()
    return render_template('upload.html', cars=cars)

# Edit Car
@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template('upload.html', car=car, cars=Car.query.all())

# Delete Car
@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    car = Car.query.get(car_id)
    if car:
        db.session.delete(car)
        db.session.commit()
        flash('Car deleted successfully!', 'success')
    return redirect(url_for('upload'))

# Delete All Cars
@app.route('/delete_all', methods=['POST'])
def delete_all():
    db.session.query(Car).delete()
    db.session.commit()
    flash('All cars deleted successfully!', 'success')
    return redirect(url_for('upload'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
