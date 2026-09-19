from app.tools.pdf_loader import PDFLoader

from app.tools.pdf_paper_extractor import PDFPaperExtractor

pdf_path = "test_files/sample.pdf"

# 1. Load PDF into Document

loader = PDFLoader()

document = loader.load(pdf_path)

# 2. Create PDF paper extractor

extractor = PDFPaperExtractor()

# 3. Extract abstract

abstract = extractor.extract_abstract(document)

# 4. Print result

print("=== PDF Abstract Extraction Test ===")

print(f"\nFilename: {document.filename}")

print("\n=== Extracted Abstract ===")

print(abstract)

print(f"\nAbstract Length: {len(abstract)}")

# 5. Basic validation

assert abstract != ""

assert "Pharmaceutical products are highly sensitive" in abstract

assert "1. Introduction" not in abstract

title = extractor.extract_title(document)

print("\n=== Extracted Title ===")

print(title)

print(f"\nTitle Length: {len(title)}")

assert title != ""

assert title == (

    "A hybrid approach for outlier detection in pharmaceutical "

    "cold chain logistics: A case study"

)

print("\nAll PDFPaperExtractor tests passed.")