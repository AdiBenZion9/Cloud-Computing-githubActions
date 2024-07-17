import requests

BASE_URL = "http://localhost:5001/books"

accepted_queries = {'title', 'authors', 'ISBN', 'publisher', 'publishedDate', 'genre', 'id'}


def process_queries(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        queries = [query.strip() for query in file.readlines()]

    responses = []
    s = {}
    for query in queries:
        if query[query.find('?') + 1: query.find('=')] not in accepted_queries:
            responses.append((query, f"error 422"))
            continue

        response = requests.get(f"{BASE_URL}{query}")
        s[query] = response.status_code
        if response.status_code in [200, 201]:
            responses.append((query, response.text))
        else:
            responses.append((query, f"error {response.status_code}"))
        # if response.status_code in {500, 400, 422, 415, 404}:
        #   responses.append((query, f"error {response.status_code}"))
        # else:
        #   response.raise_for_status()  # Raise an HTTPError on bad status
        #  responses.append((query, response.text))

    with open(output_file_path, 'w') as file:
        for key, value in s.items():
            file.write(f"key{key} and value{value}")
        for query, result in responses:
            file.write(f"query: {query}\nresponse: {result}\n\n")


def main():
    process_queries('../query.txt', 'response.txt')


if __name__ == "__main__":
    main()
