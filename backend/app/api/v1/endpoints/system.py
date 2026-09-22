from fastapi import APIRouter

router = APIRouter()


@router.get("/system/info")
def system_info() -> dict[str, str]:
    return {
        "product": "PlantGuard AI",
        "api_version": "v1",
        "phase": "1",
        "status": "foundation",
    }
