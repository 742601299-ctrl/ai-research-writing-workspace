from app.tools.pdf_loader import PDFLoader

loader = PDFLoader()

document = loader.load(

    "test_files/sample.pdf"

)

print("=== PDF Loader Test ===")

print(f"\nFilename: {document.filename}")

print(f"File Path: {document.file_path}")

print(f"Total Pages: {len(document.pages)}")

print(f"Full Text Length: {len(document.text)}")

print("\n=== Pages ===")

for page in document.pages:

    print(f"\nPage {page.page_number}")

    print("-" * 80)

    print(page.text[:500])

print("\n=== Full Text Preview ===")

print(document.text[:1000])

# Basic assertions

assert document.filename == "sample.pdf"

assert document.file_path == "test_files/sample.pdf"

assert len(document.pages) > 0

assert document.pages[0].page_number == 1

assert len(document.text) > 0

print("\nAll PDFLoader tests passed.")