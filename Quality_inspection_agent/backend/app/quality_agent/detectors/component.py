from .base import Detector

class ComponentDetector(Detector):
    key = "component"
    category = "component"
    title = "Component / installation inspection"
    baseline_threshold = .82

    def detect(self, image_path):
        # Installation quality cannot be reliably inferred from the presence of a
        # rectangle/edge alone. Without a trained model, this category is checklist-
        # driven and deliberately returns no visual defect to avoid false positives.
        external = self.external_findings(image_path)
        return external
