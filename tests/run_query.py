import assn3_tests
import requests


def process_queries(input_file_path, output_file_path):
    # Step 1: Read queries from the input file
    with open(input_file_path, 'r') as file:
        queries = [query.strip() for query in file.readlines()]

    # Step 2: Make HTTP GET requests with the queries
    responses = []
    for query in queries:
        try:
            response = assn3_tests.get_request(f"books{query}")
            response.raise_for_status()  # Raise an HTTPError on bad status
            responses.append((query,response.text))
        except requests.exceptions.RequestException as e:
            responses.append((query,f"error {response.status_code}"))

    # Step 3: Save responses to the output file
    with open(output_file_path, 'w') as file:
        for query, response in responses:
            file.write(f"query: {query}\n")
            file.write(f"response: {response}\n")


# Main function to read queries, make requests, and save responses
def main():
    queries_file = '../query.txt'
    responses_file = 'response.txt'
    process_queries(queries_file, responses_file)

if __name__ == "__main__":
    main()