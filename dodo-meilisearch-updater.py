#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import argparse
import os
import sys
from typing import List

def update_filterable_attributes(
    index_name: str,
    base_url: str,
    token: str,
    filterable_attributes: List[str]
) -> bool:
    """Update filterable attributes for a specific index."""
    url = f"{base_url.rstrip('/')}/indexes/{index_name}/settings/filterable-attributes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = json.dumps(filterable_attributes).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            print(f"✅ Successfully updated filterable attributes for index: {index_name}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP error for index {index_name}: {e.code} {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"❌ URL error for index {index_name}: {e.reason}")
    except Exception as e:
        print(f"❌ Error for index {index_name}: {e}")

    return False

def main():
    parser = argparse.ArgumentParser(description="Update filterable attributes for Meilisearch indexes")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("MEILISEARCH_URL", "http://meilisearch.infra.dodopayments.tech/"),
        help="Base URL of the Meilisearch instance"
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("MEILISEARCH_TOKEN"),
        help="Meilisearch API token"
    )
    parser.add_argument(
        "--indexes",
        nargs="+",
        default=["dev_test_addons"],
        help="List of indexes to update"
    )
    parser.add_argument(
        "--filterable-attributes",
        nargs="+",
        default=["business_id"],
        help="List of filterable attributes to set"
    )
    parser.add_argument(
        "--file",
        help="Path to a JSON file containing a list of indexes"
    )

    args = parser.parse_args()

    if not args.token:
        print("Error: No token provided. Use --token or set MEILISEARCH_TOKEN environment variable.")
        sys.exit(1)

    indexes = args.indexes

    # If a file is provided, read indexes from the file
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_indexes = json.load(f)
                if isinstance(file_indexes, list):
                    indexes = file_indexes
                else:
                    print(f"Error: File {args.file} does not contain a valid list of indexes.")
                    sys.exit(1)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading file {args.file}: {e}")
            sys.exit(1)

    print(f"Updating filterable attributes for {len(indexes)} indexes:")
    print(f"Filterable attributes: {args.filterable_attributes}")

    success_count = 0
    for index in indexes:
        if update_filterable_attributes(
            index_name=index,
            base_url=args.base_url,
            token=args.token,
            filterable_attributes=args.filterable_attributes
        ):
            success_count += 1

    print(f"\nSummary: Updated {success_count} out of {len(indexes)} indexes.")

    if success_count < len(indexes):
        sys.exit(1)  # Return non-zero exit code if not all indexes were updated

if __name__ == "__main__":
    main()
