#!/usr/bin/env python3
"""
Apache StreamSets Data Collector sample (offline, bundled stages only).

Builds and runs a small pipeline entirely through the REST API:

    Dev Raw Data Source (JSON)  ->  Local FS (JSON)

Only stages bundled in the image are used (dev-lib / basic-lib), so it works
without the Package Manager (whose external archive is no longer reachable).

Requires the container started via docker-compose (basic auth, admin/admin).
"""
import base64
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE = "http://localhost:18630"
AUTH = base64.b64encode(b"admin:admin").decode()
PIPELINE_TITLE = "SampleETL"
OUT_DIR = "/tmp/out"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", "Basic " + AUTH)
    req.add_header("X-Requested-By", "sdc")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as r:
        text = r.read().decode()
        return r.status, (json.loads(text) if text.strip() else None)


def wait_ready(timeout=300):
    print("Waiting for StreamSets to be ready ...")
    for _ in range(timeout // 5):
        try:
            status, _ = call("GET", "/rest/v1/system/info/currentUser")
            if status == 200:
                print("  ready.")
                return
        except (urllib.error.URLError, ConnectionError):
            pass
        time.sleep(5)
    sys.exit("StreamSets did not become ready in time.")


def _instance(defs_stages, name, library, inst, x, y, in_lanes, out_lanes, overrides, services):
    sd = next(s for s in defs_stages if s["name"] == name and s["library"] == library)
    conf = [{"name": c["name"], "value": c.get("defaultValue")} for c in sd["configDefinitions"]]
    cmap = {c["name"]: c for c in conf}
    for k, v in overrides.items():
        if k in cmap:
            cmap[k]["value"] = v
        else:
            conf.append({"name": k, "value": v})
    return {
        "instanceName": inst, "library": sd["library"], "stageName": sd["name"],
        "stageVersion": sd["version"], "configuration": conf,
        "uiInfo": {"label": inst, "xPos": x, "yPos": y, "stageType": sd["type"], "description": ""},
        "inputLanes": in_lanes, "outputLanes": out_lanes, "eventLanes": [], "services": services,
    }


def _service(defs_services, provides, overrides):
    sd = next(s for s in defs_services if s["provides"] == provides)
    conf = [{"name": c["name"], "value": c.get("defaultValue")} for c in sd["configDefinitions"]]
    cmap = {c["name"]: c for c in conf}
    for k, v in overrides.items():
        cmap[k]["value"] = v
    return {"service": sd["provides"], "serviceVersion": sd["version"], "configuration": conf}


def build_and_save():
    _, defs = call("GET", "/rest/v1/definitions")
    stages, services = defs["stages"], defs["services"]

    # (re)create an empty pipeline with a stable id
    pid = PIPELINE_TITLE
    try:
        call("PUT", f"/rest/v1/pipeline/{pid}?description=bundled-stages%20demo")
    except urllib.error.HTTPError:
        pass  # already exists

    records = "\n".join(json.dumps(r) for r in [
        {"name": "name1", "city": "Tokyo", "temp": 30},
        {"name": "name2", "city": "Osaka", "temp": 28},
        {"name": "name3", "city": "Sapporo", "temp": 22},
    ])
    parser = _service(services,
                      "com.streamsets.pipeline.api.service.dataformats.DataFormatParserService",
                      {"dataFormat": "JSON", "dataFormatConfig.jsonContent": "MULTIPLE_OBJECTS"})
    src = _instance(stages, "com_streamsets_pipeline_stage_devtest_rawdata_RawDataDSource",
                    "streamsets-datacollector-dev-lib", "DevRawDataSource_01", 60, 50,
                    [], ["laneSrc"], {"rawData": records, "stopAfterFirstBatch": True}, [parser])
    tgt = _instance(stages, "com_streamsets_pipeline_stage_destination_localfilesystem_LocalFileSystemDTarget",
                    "streamsets-datacollector-basic-lib", "LocalFS_01", 320, 50,
                    ["laneSrc"], [], {"configs.dataFormat": "JSON",
                                      "configs.dirPathTemplate": OUT_DIR,
                                      "configs.fileType": "TEXT"}, [])
    err = _instance(stages, "com_streamsets_pipeline_stage_destination_devnull_ToErrorNullDTarget",
                    "streamsets-datacollector-basic-lib", "Discard_ErrorStage", 60, 250,
                    [], [], {}, [])

    _, cfg = call("GET", f"/rest/v1/pipeline/{pid}")
    cfg["stages"] = [src, tgt]
    cfg["errorStage"] = err
    call("POST", f"/rest/v1/pipeline/{pid}", cfg)

    _, info = call("GET", f"/rest/v1/pipeline/{pid}")
    if not info.get("valid"):
        print("Pipeline is INVALID:")
        print(json.dumps(info.get("issues"), indent=2))
        sys.exit(1)
    print(f"Pipeline '{pid}' created and validated (no issues).")
    return pid


def run(pid):
    print("Starting pipeline ...")
    call("POST", f"/rest/v1/pipeline/{pid}/start")
    for _ in range(40):
        _, st = call("GET", f"/rest/v1/pipeline/{pid}/status")
        status = st["status"]
        if status in ("FINISHED", "RUN_ERROR", "STOPPED"):
            print(f"  pipeline status: {status}")
            break
        time.sleep(3)


def show_output():
    print("\n== Output written by the pipeline (/tmp/out in the container) ==")
    try:
        out = subprocess.run(
            ["docker", "exec", "streamsets", "sh", "-c", f"cat {OUT_DIR}/*"],
            capture_output=True, text=True, timeout=30)
        print(out.stdout or "(no output)")
    except Exception as e:  # noqa: BLE001
        print(f"(could not read output via docker exec: {e})")
        print(f"View it manually: docker exec streamsets cat {OUT_DIR}/*")


def main():
    wait_ready()
    pid = build_and_save()
    run(pid)
    show_output()


if __name__ == "__main__":
    main()
