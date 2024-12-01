# PocketHealth DICOM

### Steps To Run:

The app is running on Docker for ease of you, ensure you have recent version of Docker running locally.

Start the service
`docker compose up`

The service should be running on host: `0.0.0.0` and port `5001`

Swagger is set up to be on `http://0.0.0.0:5001/api/docs/`, feel free to navigate to that url for manual testing and for an overview of each input and response

If you would prefer using curl requests, the breakdown is as following:


```
POST /upload: Uploads and stores the DICOM file.
```


example curl request where file is a DICOM file:
```
curl -X 'POST' \
  'http://0.0.0.0:5001/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@IM000002'
```

```
GET /dicom-header-attribute: Retrieves header attribute data based on the DICOM tag (query parameter).
```

example curl request where filename is the filename of an uploaded DICOM file and tag is the respective DICOM tag in the format of XXXX,XXXX where each element is a hexidecimal value
```
curl -X 'GET' \
  'http://0.0.0.0:5001/dicom-header-attribute?filename=IM000001&tag=0010%2C0020' \
  -H 'accept: application/json'
```

```
GET /convert-to-png: Converts the DICOM file to a PNG and serves it.
```

example curl where filename is a DICOM file that has been uploaded and the output is the respective PNG
```
curl -X 'GET' \
  'http://0.0.0.0:5001/convert-to-png?filename=IM000002' --output output.png \
  -H 'accept: application/json'
```

### Limitations:

- Files are saved via image name so if two files share the same name, the latter will overwrite the former (ie, uploading a file named 'IM000002' and then uploading a different file but with the same file name of 'IM000002' will overwrite the former file)
- DICOM files are saved to the `/tmp` directory so the Operating System will eventually clean these up.

### Future improvements

- Integrate with a database and/or S3 for file storage.
- Be able to support converting to different formats other than PNG
- Batch uploading and downloading
- Rate limiting, file size limiting, compression of files
- Connect to a message broker (Kafka) as well as Kubernetes to handle increased load

### Rationals:
- Flask/Python - I chose this combination as it is what I am most comfortable with
- I put everything within the `app.py` for simplicity reasons
- I used `tmp` to store files so that we don't have to worry about any issues regarding stale data that didn't get cleaned up as the OS will ensure they are removed

### Notes:
- I generated the `test_app.py` using ChatGPT -- while it was not perfect, it got me 80% of the way there and I did the rest. I believe ChatGPT is a great helper tool to validate my code as well as set up a lot of the testing boilerplate.
