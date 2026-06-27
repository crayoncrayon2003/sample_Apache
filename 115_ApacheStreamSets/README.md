# about
Apache StreamSets Data Collector sample. A small pipeline is built and run
entirely from bundled stages (no Package Manager needed):

```
Dev Raw Data Source (JSON)  ->  Local FS (JSON)
```

# build and run
```bash
docker compose up -d
```
Login (UI): http://localhost:18630  (user: `admin`, password: `admin`)

## Notes on the image version
* `4.0.0+`  : paid service (requires Control Hub).
* `3.17 - 3.22.2` : open source, but require **online activation** (an RSA-signed
  code from the StreamSets cloud), which is unreachable offline -> pipelines
  cannot be created.
* `3.16.1` (used here) : last release before the activation requirement, so it
  runs fully offline.

The image also defaults to `http.authentication=aster` (cloud login); this sample
overrides it to local `basic` auth so the UI/REST work offline with `admin/admin`.
The Package Manager still cannot download extra stage libraries (its archive at
`archives.streamsets.com` now returns AccessDenied), so this sample sticks to the
bundled `dev-lib` / `basic-lib` stages.

# run the sample pipeline
## option A: script (REST API)
Builds the pipeline, validates it, runs it, and prints the output:
```bash
python3 sample.py
```
Expected output:
```
{"name":"name1","city":"Tokyo","temp":30}
{"name":"name2","city":"Osaka","temp":28}
{"name":"name3","city":"Sapporo","temp":22}
```

## option B: import in the UI
1. Open http://localhost:18630 and log in (`admin`/`admin`).
2. Pipelines -> Import -> upload `SampleETL.json`.
3. Open the pipeline and click **Start**.
4. View the result inside the container:
   ```bash
   docker exec streamsets cat /tmp/out/*
   ```

# down
```bash
docker compose down
```
