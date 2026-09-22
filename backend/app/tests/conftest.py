import os
import tempfile
from pathlib import Path

# Isolate test DB/storage before app imports bind settings.
_tmp = Path(tempfile.mkdtemp(prefix="plantguard_test_"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'test.db').as_posix()}"
os.environ["LOCAL_STORAGE_PATH"] = str(_tmp / "storage")
os.environ["MODEL_REGISTRY_PATH"] = str(_tmp / "models")
os.environ["AUTO_BOOTSTRAP_MODEL"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["LOG_JSON"] = "false"

from app.core.config import get_settings

get_settings.cache_clear()
