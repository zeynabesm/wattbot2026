import pandas as pd
import requests
from pathlib import Path


#  metadata
df = pd.read_csv("data/metadata.csv")


# documents folder if it does not exist
documents_folder = Path("data/documents")
documents_folder.mkdir(parents=True, exist_ok=True)


#  each document
for _, row in df.iterrows():

    document_id = row["id"]
    url = row["url"]

    file_path = documents_folder / f"{document_id}.pdf"

    #  if the file already exists
    if file_path.exists():
        print(f"Already exists: {document_id}")
        continue

    print(f"Downloading: {document_id}")

    try:

        # Try the real URL
        response = requests.get(url, timeout=60)

        content_type = response.headers.get("Content-Type", "")

        is_pdf = (
            response.status_code == 200
            and "application/pdf" in content_type
            and response.content[:5] == b"%PDF-"
        )

        #  is not a PDF, check for arXiv /abs/ URL
        if not is_pdf and "/abs/" in url and "arxiv.org" in url:

            pdf_url = url.replace("/abs/", "/pdf/")

            print(f"Trying arXiv PDF: {pdf_url}")

            response = requests.get(pdf_url, timeout=60)

            content_type = response.headers.get("Content-Type", "")

            is_pdf = (
                response.status_code == 200
                and "application/pdf" in content_type
                and response.content[:5] == b"%PDF-"
            )

        #  Save if - valid PDF
        if is_pdf:

            file_path.write_bytes(response.content)

            print(f"Downloaded PDF: {document_id}")

        else:

            print(
                f"Could not download a valid PDF: "
                f"{document_id}"
            )

    except Exception as e:

        print(f"Error downloading {document_id}: {e}")