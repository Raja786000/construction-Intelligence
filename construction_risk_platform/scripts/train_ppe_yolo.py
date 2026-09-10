import argparse
from pathlib import Path

def train_yolo(dataset_dir: str, epochs: int = 50, batch_size: int = 16, model_name: str = "yolov8n.pt"):
    print("=" * 65)
    print(" 🛠️  CONSTRUCTION PPE SAFETY MODEL TRAINER (Kaggle/Roboflow)")
    print("=" * 65)
    print(f"Dataset Path: {dataset_dir}")
    print(f"Epochs: {epochs} | Batch Size: {batch_size}")
    
    try:
        from ultralytics import YOLO
        model = YOLO(model_name)
        data_yaml = Path(dataset_dir) / "data.yaml"
        if not data_yaml.exists():
            print(f"[Error] data.yaml not found in {dataset_dir}. Please provide a valid YOLO format dataset.")
            return

        print(f"Starting YOLO training on {data_yaml}...")
        model.train(data=str(data_yaml), epochs=epochs, batch=batch_size, imgsz=640)
        print("Training complete! Save best weights to risk_model/yolo11n.pt")
    except Exception as e:
        print(f"[Training Info] To train with GPU, install ultralytics and torch: pip install ultralytics torch. Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLO on Construction Safety Dataset")
    parser.add_argument("--dataset_dir", type=str, default="./datasets/construction_safety")
    parser.add_argument("--epochs", type=int, default=50)
    args = parser.parse_args()
    train_yolo(args.dataset_dir, args.epochs)
