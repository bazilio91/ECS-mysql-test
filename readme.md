### ECS mysql python test
An effort to combine ECS (esper) pattern & mysql native python connector.

Running:
```
docker-compose up -d
pip install -r requirments.txt
python -m unittest tests/main_test.py 
```

For explanations see: [tests/main_test.py](tests/main_test.py) 

Next steps:
- use sqlalchemy for change detections and safer updates?
