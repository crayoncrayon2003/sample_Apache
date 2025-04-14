import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Original Item1 model for '/endpoint1/'
class Item1(BaseModel):
    name: str
    temperature: float
    humidity: float

# Transformed Item2 model that fits your required output structure
class Item2(BaseModel):
    id: str = "endpoint2"
    type: str = "sampletype"
    name: Dict[str, str]
    temp: Dict[str, str]
    humi: Dict[str, str]

@app.get("/endpoint1/")
def read_endpoint1():
    print("this is endpoint1 get")
    ret = {
        "name": "endpoint1",
        "temperature": 20,
        "humidity": 50
    }
    return ret

@app.post("/endpoint1/")
def create_endpoint1(item: Item1):
    print("this is endpoint1 post")
    print(item)
    return item

@app.get("/endpoint2/")
def read_endpoint2():
    print("this is endpoint2 get")
    ret = {
        "id": "endpoint2",
        "type": "sampletype",
        "name": {
            "value": "endpoint2",
            "type": "TEXT"
        },
        "temp": {
            "value": 20,
            "type": "Integer"
        },
        "humi": {
            "value": 50,
            "type": "Integer"
        }
    }
    return ret

# Now, `Item2` is expected for POST /endpoint2/
@app.post("/endpoint2/")
def create_endpoint2(item: Item2):
    print("this is endpoint2 post")
    print(item)
    return item

def main():
    uvicorn.run(app, host="127.0.0.1", port=5050)

if __name__ == "__main__":
    main()
