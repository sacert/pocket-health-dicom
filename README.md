# PocketHealth DICOM Service

This repository provides a simple Flask-based service for uploading, processing, and retrieving data from DICOM files. It includes REST endpoints for uploading DICOM files, retrieving metadata, and converting files to PNG format. The service also features Swagger documentation for easy exploration of available endpoints.



## Getting Started

### Prerequisites

- **Docker (recommended):** Ensure Docker and Docker Compose are installed on your system.
- **Python (alternative):** Install Python 3.11 or higher if you plan to run the service without Docker.

### Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/sacert/pocket-health-dicom.git
   cd pocket-health-dicom
   ```

2. Copy the example environment file and adjust it for your environment:
   ```bash
   cp .env.example .env
   ```



## Running the Service

### With Docker (Recommended)

1. Build and start the service using Docker Compose:
   ```bash
   docker compose up
   ```

2. The service will be available at `http://0.0.0.0:5001`.
3. Run tests with:
   ```bash
   docker compose run app pytest .
   ```


---

### Without Docker

1. Install the Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Run the Flask application:
   ```bash
   flask run -h 0.0.0.0 -p 5001
   ```
3. Run tests with:
   ```bash
   pytest
   ```



## REST Endpoints

### **POST** `/upload`

Uploads and stores a DICOM file.

**Body Parameters:**
- `file` (required): The path to the DICOM file.

**Example Request:**
```bash
curl -X 'POST' \
  'http://0.0.0.0:5001/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path/to/your/file.dcm'
```

---

### **GET** `/dicom-header-attribute`

Retrieves the value of a specific DICOM header attribute based on the provided tag.

**Query Parameters:**
- `filename` (required): The name of the uploaded DICOM file.
- `tag` (required): The DICOM tag in the format `XXXX,XXXX` (hexadecimal).

**Example Request:**
```bash
curl -X 'GET' \
  'http://0.0.0.0:5001/dicom-header-attribute?filename=example.dcm&tag=0010,0010' \
  -H 'accept: application/json'
```

---

### **GET** `/convert-to-png`

Converts a DICOM file to PNG format and returns the PNG image.

**Query Parameters:**
- `filename` (required): The name of the uploaded DICOM file.

**Example Request:**
```bash
curl -X 'GET' \
  'http://0.0.0.0:5001/convert-to-png?filename=example.dcm' --output example.png \
  -H 'accept: application/json'
```



## Swagger Documentation

Swagger documentation is available at:
```
http://0.0.0.0:5001/api/docs/
```

Once the server is running, navigate to this URL to explore and test the API endpoints.


## Limitations

1. **File Overwriting:** Files with the same name will overwrite each other. For example, uploading two files named `example.dcm` will result in the second file replacing the first.
2. **Temporary Storage:** DICOM files are stored in the `/tmp` directory. These files will be cleaned up by the operating system over time.



## Future Improvements

- **File Storage:** Integrate with a database or S3 for persistent file storage.
- **File Formats:** Support conversion to formats other than PNG.
- **Batch Processing:** Add support for batch uploads and downloads.
- **Enhancements:** Implement rate limiting, file compression, improved file size handling, and the ability to view all uploaded files.
- **Scalability:** Use a message broker (e.g., Kafka) and Kubernetes to scale the service for increased load.


## Why These Choices?

- **Flask and Python:** Selected for their simplicity and familiarity.
- **File Storage:** Temporary files are stored in `/tmp` to avoid issues with stale data, as the operating system will automatically clean up these files.
- **Code Simplicity:** All logic is contained within `app.py` for straightforward maintenance and clarity.


## Notes

- Unit tests were generated with the help of ChatGPT, which assisted in creating boilerplate code and validation. The tests were then refined manually to ensure correctness and reliability.
