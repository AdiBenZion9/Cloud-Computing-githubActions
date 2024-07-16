import requests

# Define the URL for books API
BASE_URL = "http://localhost:5001/books"


def process_queries(input_file_path, output_file_path):
    # Step 1: Read queries from the input file
    response = None
    with open(input_file_path, 'r') as file:
        queries = [query.strip() for query in file.readlines()]

    # Step 2: Make HTTP GET requests with the queries
    responses = []
    for query in queries:
        try:
            response = requests.get(f"{BASE_URL}{query}")
            response.raise_for_status()  # Raise an HTTPError on bad status
            responses.append((query, response.text))
        except requests.exceptions.RequestException as e:
            responses.append((query, f"error {response.status_code}"))

    # Step 3: Save responses to the output file
    with open(output_file_path, 'w') as file:
        for query, response in responses:
            file.write(f"query: {query}\n")
            file.write(f"response: {response}\n")


# Main function to read queries, make requests, and save responses
def main():
    process_queries('../query.txt', 'response.txt')


if __name__ == "__main__":
    main()
