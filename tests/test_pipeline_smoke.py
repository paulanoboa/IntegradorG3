"""Prueba de humo liviana para las etapas del pipeline sobre datos sintéticos."""
from datetime import date
from pathlib import Path
import tempfile
import unittest

import pandas as pd

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pipeline


class PipelineSmokeTest(unittest.TestCase):
    def test_all_stages_on_small_synthetic_dataset(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.ROOT = root
            pipeline.RAW = root / "data" / "raw"
            pipeline.PROCESSED = root / "data" / "processed"
            pipeline.METRICS = root / "results" / "metrics"
            pipeline.REPORTS = root / "results" / "reports"
            pipeline.FIGURES = root / "results" / "figures"
            pipeline.MODELS = root / "models"
            source_dir = pipeline.RAW / "data2021"
            source_dir.mkdir(parents=True)

            locations = [("AZUAY", "CUENCA"), ("GUAYAS", "GUAYAQUIL"),
                         ("PICHINCHA", "QUITO"), ("MANABI", "MANTA")]
            rows = []
            for month_index in range(18):
                year = 2021 + month_index // 12
                month = month_index % 12 + 1
                for location_index, (province, canton) in enumerate(locations):
                    count = 1 + ((month_index * 5 + location_index * 7) % 21)
                    rows.extend({
                        "Fecha": date(year, month, 1).strftime("%d/%m/%Y"),
                        "provincia": province,
                        "Canton": canton,
                        "Cod_Parroquia": f"{10000 + location_index:06d}",
                        "Parroquia": canton,
                        "Servicio": "Seguridad Ciudadana",
                        "Subtipo": "Robo",
                    } for _ in range(count))
            pd.DataFrame(rows).to_csv(source_dir / "incidentes_demo.csv", sep=";", index=False)

            pipeline.run_stage("all")
            logger = pipeline.logging.getLogger("ecuador_pipeline")
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()
            metrics_path = pipeline.METRICS / "global_metrics.csv"
            risk_path = pipeline.PROCESSED / "province_risk.csv"
            forecast_path = pipeline.PROCESSED / "forecast_months.csv"
            self.assertTrue(metrics_path.exists())
            self.assertTrue(risk_path.exists())
            self.assertTrue(forecast_path.exists())
            self.assertEqual(len(pd.read_csv(risk_path)), 4)
            self.assertEqual(len(pd.read_csv(forecast_path)), 12)
            self.assertTrue((pipeline.FIGURES / "confusion_random_forest.png").exists())
            self.assertTrue((pipeline.FIGURES / "roc_xgboost.png").exists())


if __name__ == "__main__":
    unittest.main()
