import requests

# Define the URL for books API
BASE_URL = "http://localhost:5001/books"

books_ids = []


def test_post_books():
    books = [
        {"title": "Adventures of Huckleberry Finn", "ISBN": "9780520343641", "genre": "Fiction"},
        {"title": "The Best of Isaac Asimov", "ISBN": "9780385050784", "genre": "Science Fiction"},
        {"title": "Fear No Evil", "ISBN": "9780394558783", "genre": "Biography"}
    ]
    for book in books:
        response = requests.post(BASE_URL, json=book)
        assert response.status_code == 201
        response_data = response.json()
        assert 'ID' in response_data
        books_ids.append(response_data['ID'])
    assert len(set(books_ids)) == 3  # Check if all IDs are unique


def test_get_book_by_id():
    first_book_id = books_ids[0]
    response = requests.get(f"{BASE_URL}/{first_book_id}")
    assert response.status_code == 200
    assert response.json()['authors'] == 'Mark Twain'


def test_get_books():
    response = requests.get(BASE_URL)
    assert response.status_code == 404
    assert len(response.json()) == 3  # Expecting 3 books


def test_post_invalid_book():
    book = {"title": "No such book", "ISBN": "0000001111111", "genre": "Biography"}
    response = requests.post(BASE_URL, json=book)
    assert response.status_code in [400, 500]


def test_delete_book():
    second_book_id = books_ids[1]
    response = requests.delete(f"{BASE_URL}/{second_book_id}")
    assert response.status_code == 200


def test_get_deleted_book():
    second_book_id = books_ids[1]
    response = requests.get(f"{BASE_URL}/{second_book_id}")
    assert response.status_code == 404


def test_post_unacceptable_genre_book():
    book = {"title": "The Greatest Joke Book Ever", "authors": "Mel Greene", "ISBN": "9780380798490", "genre": "Jokes"}
    response = requests.post(BASE_URL, json=book)
    assert response.status_code == 422

