# import uuid
# import os
# import shutil
# import torch
# import logging
# import asyncio
# import tempfile
# import glob
# from fastapi import APIRouter, UploadFile, Form
# from fastapi.responses import FileResponse, JSONResponse
# from PIL import Image
# from diffusers import FluxFillPipeline
# from app.config.settings import settings

# router = APIRouter()
# logger = logging.getLogger(__name__)

# # ======================
# # Force HuggingFace + tmp dirs
# # ======================
# workspace = settings.HF_HOME or "/workspace/huggingface"
# base_model_dir = "/workspace/flux_model"   # ✅ where models are cached
# tmpdir = os.path.join(workspace, "tmp")
# os.makedirs(tmpdir, exist_ok=True)

# # Override environment + tempfile
# os.environ["TMPDIR"] = tmpdir
# tempfile.tempdir = tmpdir
# logger.info(f"✅ TMPDIR forced to {tmpdir}")

# # Global pipeline + loading flag
# pipe = None
# loading = False


# def check_system_resources():
#     """Check disk quota and GPU memory before loading model"""
#     os.makedirs(workspace, exist_ok=True)
#     total, used, free = shutil.disk_usage(workspace)

#     logger.info(f"HF_HOME={settings.HF_HOME}, HF_HUB_CACHE={settings.HF_HUB_CACHE}, TRANSFORMERS_CACHE={settings.TRANSFORMERS_CACHE}")
#     logger.info(f"TEMP dir in use = {tempfile.gettempdir()}")

#     disk_info = {
#         "total_gb": round(total / 1e9, 1),
#         "used_gb": round(used / 1e9, 1),
#         "free_gb": round(free / 1e9, 1)
#     }

#     gpu_info = None
#     if torch.cuda.is_available():
#         props = torch.cuda.get_device_properties(0)
#         gpu_info = {"device": props.name, "vram_gb": round(props.total_memory / 1e9, 1)}

#     return disk_info, gpu_info


# def get_snapshot_dir():
#     """Find the actual snapshot directory inside HuggingFace cache"""
#     snapshots_root = os.path.join(base_model_dir, "models--black-forest-labs--FLUX.1-Fill-dev", "snapshots")
#     if not os.path.exists(snapshots_root):
#         raise RuntimeError(f"No snapshot folder found in {snapshots_root}")

#     snapshots = glob.glob(f"{snapshots_root}/*")
#     if not snapshots:
#         raise RuntimeError(f"No snapshot directories inside {snapshots_root}")

#     snapshot_dir = snapshots[0]
#     logger.info(f"📂 Using snapshot directory: {snapshot_dir}")
#     return snapshot_dir


# async def load_pipeline():
#     """Load Hugging Face pipeline (local snapshot first, fallback to Hub)"""
#     global pipe, loading
#     if pipe is None and not loading:
#         try:
#             loading = True
#             disk_info, gpu_info = check_system_resources()
#             logger.info(f"[Disk] {disk_info}")
#             if gpu_info:
#                 logger.info(f"[GPU] {gpu_info}")

#             device = "cuda" if torch.cuda.is_available() else "cpu"
#             dtype = torch.float16 if device == "cuda" else torch.float32

#             try:
#                 snapshot_dir = get_snapshot_dir()
#                 pipe = FluxFillPipeline.from_pretrained(snapshot_dir, torch_dtype=dtype).to(device)
#                 logger.info("✅ FluxFillPipeline loaded from local snapshot.")
#             except Exception as e:
#                 logger.warning(f"⚠️ Local snapshot not available, falling back to HuggingFace Hub: {e}")
#                 pipe = FluxFillPipeline.from_pretrained(
#                     "black-forest-labs/FLUX.1-Fill-dev",
#                     token=settings.HF_TOKEN,
#                     torch_dtype=dtype,
#                     cache_dir=base_model_dir
#                 ).to(device)
#                 logger.info("✅ FluxFillPipeline loaded from HuggingFace Hub.")

#         except Exception as e:
#             logger.error(f"❌ Failed to load model: {e}", exc_info=e)
#             raise
#         finally:
#             loading = False


# def prepare_outpaint_inputs(orig: Image.Image, target_w: int, target_h: int):
#     """Prepare expanded canvas and mask (black=keep original, white=generate new)"""
#     # New blank canvas
#     new_img = Image.new("RGB", (target_w, target_h), (0, 0, 0))
#     new_mask = Image.new("L", (target_w, target_h), 255)  # white = editable

#     # Center original image
#     x = (target_w - orig.width) // 2
#     y = (target_h - orig.height) // 2
#     new_img.paste(orig, (x, y))

#     # Mask: black where original image is pasted (keep original)
#     black_patch = Image.new("L", (orig.width, orig.height), 0)
#     new_mask.paste(black_patch, (x, y))

#     return new_img, new_mask


# # Background preload at startup
# @router.on_event("startup")
# async def preload_pipeline():
#     asyncio.create_task(load_pipeline())


# @router.post("/outpaint")
# async def outpaint_image(
#     file: UploadFile,
#     width: int = Form(720),
#     height: int = Form(1280),
#     steps: int = Form(20),
#     prompt: str = Form("expand the scene naturally"),
# ):
#     """Expand an image by outpainting with FLUX model"""
#     global pipe

#     if pipe is None:
#         await load_pipeline()

#     try:
#         input_path = os.path.join(tmpdir, f"{uuid.uuid4()}_{file.filename}")
#         with open(input_path, "wb") as f:
#             f.write(await file.read())

#         orig = Image.open(input_path).convert("RGB")

#         # 👇 expand + create mask
#         expanded_img, mask = prepare_outpaint_inputs(orig, width, height)

#         result = pipe(
#             prompt=prompt,
#             image=expanded_img,
#             mask_image=mask,
#             height=height,
#             width=width,
#             num_inference_steps=steps,
#             guidance_scale=3.5
#         ).images[0]

#         output_path = os.path.join(tmpdir, f"{uuid.uuid4()}_outpaint.png")
#         result.save(output_path)

#         return FileResponse(output_path, media_type="image/png", filename="outpaint_result.png")

#     except Exception as e:
#         logger.error(f"❌ Outpaint failed: {e}", exc_info=e)
#         return JSONResponse(status_code=500, content={"error": "OUTPAINT_FAILED", "message": str(e)})


# @router.get("/outpaint/status")
# async def outpaint_status():
#     """Check if model is loaded, loading, and system resources"""
#     global pipe, loading
#     disk_info, gpu_info = check_system_resources()

#     return {
#         "model_loaded": pipe is not None,
#         "loading": loading,
#         "disk": disk_info,
#         "gpu": gpu_info or {"device": "cpu", "vram_gb": None},
#         "tmpdir": tempfile.gettempdir()
#     }
