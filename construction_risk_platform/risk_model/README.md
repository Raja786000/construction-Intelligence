# Risk Model
Image, recorded-video and webcam construction-risk CV layer.

Run from project root:
`python -m risk_model.cli --image test.jpg --save risk_output.jpg`
`python -m risk_model.cli --camera`
`python -m risk_model.cli --video test.mp4 --save monitored.mp4`
`uvicorn risk_model.api:app --reload --port 8001`

IMPORTANT: yolo11n.pt is a general pretrained YOLO model. It does not reliably detect construction PPE classes such as helmet/vest. For real PPE alerts use a custom-trained construction YOLO `.pt` model and set `RISK_MODEL_WEIGHTS` to its path. Edit config.py class aliases to match your model's names.
