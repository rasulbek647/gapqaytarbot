from aiogram import Router

from .users.start import router as start_router
from .users.register import router as register_router

router = Router()

router.include_router(start_router)
router.include_router(register_router)
