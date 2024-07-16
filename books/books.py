import pymongo
from flask import Flask, request
from flask_restful import Api, Resource
import requests
import uuid


app1 = Flask(__name__)
api = Api(app1)


# Connect to MongoDB
client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["Library"]
books_collection = db["Books"]
ratings_collection = db["Ratings"]
books_ids = db["BooksIds"]


class Books(Resource):
    def get(self):
        args = request.args
        try:
            if args:
                query = {key: value for key, value in args.items()}
                filtered_books = list(books_collection.find(query, {'_id': 0}))
            else:
                filtered_books = list(books_collection.find({}, {'_id': 0}))
            return filtered_books, 200
        except Exception as e:
            return {'Error fetching data': str(e)}

    def post(self):
        try:
            # Check if the mediaType is JSON
            if request.headers['Content-Type'] != 'application/json':
                return {'error': 'Unsupported Media Type: Only JSON is supported.'}, 415

            data = request.json

            # Check if there's a missing field
            if not all(field in data for field in ['title', 'ISBN', 'genre']):
                return {'message': 'Unprocessable entity: Missing required fields'}, 422

            if not data['title'].split() or not data['ISBN'].split():
                return {'message': 'Unprocessable entity: Empty fields are not accepted'}, 422

            if not data['ISBN'].isdigit() or len(data['ISBN']) != 13:
                return {'message': 'Unprocessable entity: ISBN must be only 13 numbers'}, 422

            # Check for invalid genre
            accepted_genres = ['Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other']
            if data['genre'] not in accepted_genres:
                return {'message': 'Unprocessable entity: Invalid genre value'}, 422

            # Search for the book by ISBN
            if books_collection.find_one({'ISBN': data['ISBN']}):
                return {'message': 'Error: Book already exists'}, 422

            else:
                try:
                    # Fetch additional book information from Google Books API
                    google_books_url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{data["ISBN"]}'
                    response1 = requests.get(google_books_url)
                    google_books_data = response1.json()['items'][0]['volumeInfo'] if response1.ok and 'items' in response1.json() else {}
                    if not google_books_data:
                        return {'message': 'No data found for given ISBN'}, 400
                except Exception as e:
                    return {'message': f'Error fetching book data from Google Books API:{str(e)}'}, 500
                    # Fetch additional book information from Google Books API
                authors = ' and '.join(google_books_data.get('authors', ['missing']))
                publisher = google_books_data.get('publisher', 'missing')
                publishedDate = check_date_format(google_books_data.get('publishedDate', 'missing'))

                while True:
                    book_id = str(uuid.uuid4())  # generate a unique id for each book
                    if books_ids.find_one({'BookID': book_id}) is None:
                        books_ids.insert_one({'BookID': book_id})
                        break

                book = {
                    'title': data['title'],
                    'authors': authors,
                    'ISBN': data['ISBN'],
                    'genre': data['genre'],
                    'publisher': publisher,
                    'publishedDate': publishedDate,
                    'id': book_id
                }
                books_collection.insert_one(book)
                # Create a rating space for this book
                ratings_collection.insert_one({'id': book_id, 'values': [], 'average': 0.0, 'title': data['title']})
                print('Book added successfully to the library!')
                return {'ID': book_id}, 201
        except Exception as e:
            return {'Invalid JSON file': str(e)}, 422


class BooksId(Resource):
    def get(self, id):
        book = books_collection.find_one({'id': id}, {'_id': 0})
        if not book:
            return {'message': 'Not Found: Book not found'}, 404
        return book, 200

    def put(self, id):
        try:
            # Check if the book exists
            book = books_collection.find_one({'id': id})
            if not book:
                return {'message': 'Not Found: Book not found'}, 404

            # Check if the mediaType is JSON
            if request.headers['Content-Type'] != 'application/json':
                return {'error': 'Unsupported Media Type: Only JSON is supported.'}, 415

            # Get the JSON payload from the request
            data = request.json

            fields = ['title', 'ISBN', 'genre', 'authors', 'publisher', 'publishedDate', 'id']

            # Check if there's a missing field
            if not all(field in data for field in fields):
                return {'message': 'Unprocessable entity: Missing required fields'}, 422

            for field in fields:
                if not data[f'{field}'].split():
                    return {'message': 'Unprocessable entity: Empty fields are not accepted'}, 422

            if not data['ISBN'].isdigit() or len(data['ISBN']) != 13:
                return {'message': 'Unprocessable entity: ISBN must be only 13 numbers'}, 422

            # Check for invalid genre
            accepted_genres = ['Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other']
            if data['genre'] not in accepted_genres:
                return {'message': 'Unprocessable entity: Invalid genre value'}, 422

            # Update the book fields
            update_fields = {key: data[key] for key in ['title', 'authors', 'genre', 'publisher', 'publishedDate'] if
                             key in data}
            books_collection.update_one({'id': id}, {'$set': update_fields})
            ratings_collection.update_one({'id': id}, {'$set': {'title': data.get('title', book['title'])}})
            return {'ID': id}, 200

        except Exception as e:
            return {'Invalid JSON file': str(e)}, 422

    def delete(self, id):
        delete_result = books_collection.delete_one({'id': id})
        if delete_result.deleted_count == 0:
            return {'message': 'Not Found: Book not found'}, 404
        ratings_collection.delete_one({'id': id})
        return {'ID': id}, 200


class Ratings(Resource):
    def get(self):
        book_id = request.args.get('id')
        if book_id:
            rating = ratings_collection.find_one({'id': book_id}, {'_id': 0})
            if not rating:
                return {'message': 'Not Found: book not found'}, 404
            return [rating], 200
        else:
            all_ratings = list(ratings_collection.find({}, {'_id': 0}))
            return all_ratings, 200


class RatingsId(Resource):
    def get(self, id):
        rating = ratings_collection.find_one({'id': id}, {'_id': 0})
        if rating:
            return rating, 200
        else:
            return {'message': 'Not Found: book not found'}, 404


class RatingsIdValues(Resource):
    def post(self, id):
        try:
            if request.headers['Content-Type'] != 'application/json':
                return {'error': 'Unsupported Media Type: Only JSON is supported.'}, 415

            data = request.json

            # Check if there's a missing field
            if 'value' not in data:
                return {'message': 'Unprocessable entity: You should enter a value field'}, 422

            value = data.get('value')

            if value not in [1, 2, 3, 4, 5]:
                return {'message': 'Unprocessable entity: A value should be a 1-5 integer'}, 422

            result = ratings_collection.find_one_and_update(
                {'id': id},
                {'$push': {'values': data['value']}},
                return_document=pymongo.ReturnDocument.AFTER
            )
            if result:
                avg = sum(result['values']) / len(result['values'])
                ratings_collection.update_one({'id': id}, {'$set': {'average': avg}})
                return {'Current average': avg}, 201
            else:
                return {'message': 'Not Found: book not found'}, 404
        except Exception as e:
            return {'Missing value field': str(e)}, 422


class TopBooks(Resource):
    def get(self):
        # Compute the top-rated books dynamically
        top_books = self.compute_top_books()

        if top_books:
            return top_books, 200
        else:
            return [], 200

    def compute_top_books(self):
        # Find ratings with at least 3 values and calculate averages
        ratings = list(ratings_collection.find({'values': {'$exists': True, '$not': {'$size': 0}}}))
        ratings = [r for r in ratings if len(r['values']) >= 3]
        sorted_ratings = sorted(ratings, key=lambda x: x['average'], reverse=True)

        top_books = sorted_ratings[:3]
        if len(sorted_ratings) > 3:
            threshold_average = top_books[-1]['average']
            additional_books = [r for r in sorted_ratings[3:] if r['average'] == threshold_average]
            top_books.extend(additional_books)

        result = [{
            'id': book['id'],
            'title': book['title'],
            'average': book['average']
        } for book in top_books]
        return result


def check_date_format(date_str):
    # Check if the length of the string is either 4 (for 'yyyy') or 10 (for 'yyyy-mm-dd')
    if len(date_str) == 4 or len(date_str) == 10:
        if len(date_str) == 4:
            # Check if all characters in the string are digits
            if date_str.isdigit():
                return date_str
        elif len(date_str) == 10:
            # Check if the first 4 characters are digits and the 5th and 8th characters are '-'
            if date_str[:4].isdigit() and date_str[4] == '-' and date_str[7] == '-':
                return date_str
    return "missing"


api.add_resource(Books, "/books")
api.add_resource(BooksId, "/books/<string:id>")
api.add_resource(Ratings, "/ratings")
api.add_resource(RatingsId, "/ratings/<string:id>")
api.add_resource(RatingsIdValues, "/ratings/<string:id>/values")
api.add_resource(TopBooks, "/top")

if __name__ == '__main__':
    app1.run(host="0.0.0.0", port=5001, debug=True)
