# ARGUS - Technical Design & Interview Questions

## 1. How would you process one million documents without overwhelming the server?
**Answer:** I would decouple the upload API from the processing engine using Celery and Redis. When a user uploads a file, the API simply saves it to object storage (like AWS S3) or disk, creates a 'QUEUED' record in the database, and drops a task into the Redis queue. The API responds immediately, freeing up web server resources. I would horizontally scale the Celery worker containers based on the queue depth to process documents concurrently without impacting the API's availability.

## 2. How would you improve OCR accuracy for poor-quality scanned documents?
**Answer:** I would implement an image preprocessing pipeline using OpenCV before passing the image to Tesseract. This would include:
1. Grayscale conversion and binarization (Otsu's thresholding).
2. Deskewing to fix rotated pages.
3. Noise removal (median blurring).
4. Using Tesseract's LSTM models with custom configuration flags (e.g., --oem 1).
5. If budget allows, fallback to a cloud OCR service (like AWS Textract or Google Document AI) for low-confidence pages.

## 3. How would you prevent two workers from processing the same document simultaneously?
**Answer:** By default, Celery queues guarantee that a task is delivered to only one worker. However, to prevent duplicate processing due to network retries, I would use a **Distributed Lock** via Redis (like edis-py's Lock). When a worker picks up a task, it attempts to acquire a lock using the document_id as the key. If it fails to acquire the lock, it means another worker is already processing it, so it safely aborts.

## 4. How would you identify conflicting information across 10,000 documents?
**Answer:** Comparing 10,000 documents pairwise (N^2) is computationally impossible. Instead, I would group documents by metadata (e.g., Company Name and Invoice Number) into 'Clusters'. Within each cluster, I would only compare documents against a 'Canonical' or 'Baseline' document, or use an N-way diff algorithm. I could also build a dependency graph where nodes are documents and edges are shared entities, allowing me to traverse and identify isolated or conflicting nodes.

## 5. How would you optimize search performance with millions of database records?
**Answer:** I would use a dedicated search engine like Elasticsearch or OpenSearch. If restricted to PostgreSQL, I would use a GIN (Generalized Inverted Index) on the 	o_tsvector column and partition the table by organization or date to keep the index size manageable.

## 6. How would you redesign the platform to support multiple organizations?
**Answer:** I would implement a 	enant_id (Organization ID) on every database table. All API queries would automatically filter by the 	enant_id extracted from the user's JWT token. For enterprise clients, I would implement Row-Level Security (RLS) directly in PostgreSQL to guarantee data isolation at the database engine level, even if the application code has a bug.

## 7. How would you test an extraction algorithm when the correct output is not always obvious?
**Answer:** I would use a combination of deterministic testing and statistical evaluation. I would build a 'Gold Standard' dataset of 100 manually annotated documents. I would write a testing script that runs the extraction engine and calculates Precision, Recall, and F1-Score against the annotations. For CI/CD, I would enforce a minimum F1-Score threshold (e.g., 90%) to prevent regressions.

## 8. How would you prevent malicious files from compromising the application?
**Answer:** File uploads are highly dangerous.
1. Verify MIME types (don't trust the extension).
2. Sanitize filenames to prevent path traversal.
3. Run the extraction process inside a sandboxed environment (like a separate Docker container with no network access) to prevent Remote Code Execution vulnerabilities in libraries like PyMuPDF.
4. Scan files with ClamAV.

## 9. How would you design a reliable document-processing pipeline that supports retries?
**Answer:** Use a Task Queue (Celery) with Exponential Backoff and Jitter. If a task fails (e.g., due to a temporary database connection drop), it should retry up to 3 times. If it still fails, it moves to a Dead Letter Queue (DLQ) for manual inspection. The database should track the status (QUEUED, PROCESSING, FAILED, COMPLETED) to ensure idempotency.

## 10. How would you ensure that extracted information can always be traced back to its original source?
**Answer:** When extracting entities, I would capture the **bounding box coordinates** (if using OCR or PDF parsing) and the exact character offsets within the raw text. I would save this metadata in the ExtractedEntities table (e.g., page_number, char_start, char_end). This allows the frontend to open the original document and highlight the exact sentence where the entity was found.
