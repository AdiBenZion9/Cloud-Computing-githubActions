import requests

BASE_URL = "http://localhost:5001/books"

accepted_queries = {'title', 'authors', 'ISBN', 'publisher', 'publishedDate', 'genre', 'id'}


def process_queries(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        queries = [query.strip() for query in file.readlines()]

    responses = []
    s = {}
    for query in queries:
        if query not in accepted_queries:
            responses.append((query, f"error 422"))
            continue
        try:
            response = requests.get(f"{BASE_URL}{query}")
            s[query] = response.status_code
            if len(response.text) != 0:
                responses.append((query, response.text))
            else:
                responses.append((query, f"error {response.status_code}"))
            # if response.status_code in {500, 400, 422, 415, 404}:
            #   responses.append((query, f"error {response.status_code}"))
            # else:
            #   response.raise_for_status()  # Raise an HTTPError on bad status
            #  responses.append((query, response.text))
        except requests.exceptions.HTTPError as http_err:
            responses.append((query, f"error {http_err.response.status_code}"))
        except requests.exceptions.RequestException as req_err:
            responses.append((query, f"error {str(req_err)}"))

    with open(output_file_path, 'w') as file:
        for key in s.keys():
            file.write(str(s[key]))
        for query, result in responses:
            file.write(f"query: {query}\nresponse: {result}\n\n")


def main():
    process_queries('../query.txt', 'response.txt')


if __name__ == "__main__":
    main()
