import requests

BASE_URL = "http://localhost:5001/books"

accepted_queries = {'title', 'authors', 'ISBN', 'publisher', 'publishedDate', 'genre', 'id'}


def process_queries(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        queries = [query.strip() for query in file.readlines()]

    responses = []
    for query in queries:
        if query[query.find('?') + 1: query.find('=')] not in accepted_queries:
            responses.append((query, f"error 422"))
            continue

        response = requests.get(f"{BASE_URL}{query}")
        if response.status_code in [200, 201]:
            responses.append((query, response.text))
        else:
            responses.append((query, f"error {response.status_code}"))

    with open(output_file_path, 'w') as file:
        for query, result in responses:
            file.write(f"query: {query}\nresponse: {result}\n")


def main():
    process_queries('../query.txt', 'response.txt')


if __name__ == "__main__":
    main()
