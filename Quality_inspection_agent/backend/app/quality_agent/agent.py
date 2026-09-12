from .graph import build_graph, VISUAL_THRESHOLD
from .detectors.crack import CrackDetector
from .detectors.concrete import ConcreteDetector
from .detectors.surface import SurfaceDetector
from .detectors.component import ComponentDetector
from .detectors.corrosion import CorrosionDetector

class QualityInspectionAgent:
    def __init__(self, model_config):
        self.detectors = [
            CrackDetector(model_config["crack"]),
            ConcreteDetector(model_config["concrete"]),
            SurfaceDetector(model_config["surface"]),
            ComponentDetector(model_config["component"]),
            CorrosionDetector(model_config["corrosion"]),
        ]
        self.graph = build_graph(self.detectors)

    def inspect(self, request):
        return self.graph.invoke({"request": request})["final_result"]

    def capabilities(self):
        return {
            d.key: {
                "category": d.category,
                "title": d.title,
                "enabled": True,
                "engine": d.engine,
                "external_model_available": d.external_model_enabled,
                "model_path": str(d.optional_model_path) if d.optional_model_path else None,
                "visual_acceptance_threshold": VISUAL_THRESHOLD.get(d.category, .80),
            }
            for d in self.detectors
        }
