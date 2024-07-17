import requests

# Define the URL for books API
BASE_URL = "http://localhost:5001/books"


def process_queries(input_file_path, output_file_path):
    # Step 1: Read queries from the input file
    with open(input_file_path, 'r') as file:
        queries = [query.strip() for query in file.readlines()]

    # Step 2: Make HTTP GET requests with the queries
    responses = []
    for query in queries:
        try:
            response = requests.get(f"{BASE_URL}{query}")
            if response.status_code in {500, 400, 422, 415, 404}:
                responses.append((query, f"error {response.status_code}"))
            else:
                response.raise_for_status()  # Raise an HTTPError on bad status
                responses.append((query, response.text))
        except requests.exceptions.HTTPError as http_err:
            responses.append((query, f"error {http_err.response.status_code}"))
        except requests.exceptions.RequestException as req_err:
            responses.append((query, f"error {str(req_err)}"))

    # Step 3: Write the responses to the output file
    with open(output_file_path, 'w') as file:
        for query, result in responses:
            file.write(f"query: {query}\nresponse: {result}\n\n")


# Main function to read queries, make requests, and save responses
def main():
    process_queries('../query.txt', 'response.txt')


if __name__ == "__main__":
    main()
