# Computer Vision & Safety Monitoring Datasets

This system is configured to support standard construction site safety and PPE detection datasets from Kaggle and Roboflow.

## Supported Datasets

1. **Kaggle PPE Kit Detection**:
   - URL: `https://www.kaggle.com/code/sajjadalishah/ppe-kit-detection-construction-site-safety`
   - Description: Contains images of workers with PPE gear (Hardhat, Safety Vest, Gloves, Safety Boots, Mask, Harness).

2. **Roboflow Construction Site Safety Image Dataset**:
   - URL: `https://www.kaggle.com/datasets/snehilsanyal/construction-site-safety-image-dataset-roboflow`
   - Description: Multiclass construction safety dataset containing labeled bounding boxes for:
     - `hardhat`, `no-hardhat`, `vest`, `no-vest`, `mask`, `no-mask`, `safety harness`, `person`, `machinery`, `fire`, `smoke`.

## Training Your Custom YOLO Model

To train custom YOLO weights on these datasets:
```bash
python scripts/train_ppe_yolo.py --dataset_dir ./datasets/construction_safety --epochs 50
```

Once trained, place the output `best.pt` file inside the `risk_model/yolo11n.pt` directory path. The system will automatically detect and load your trained weights.
