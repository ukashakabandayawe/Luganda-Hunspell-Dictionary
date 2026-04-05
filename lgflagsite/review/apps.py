import os
import threading
import time
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings


def _ensure_user_working_dic_exists(user_id: int) -> None:
    try:
        from django.conf import settings as dj_settings
        from .dic_io import ensure_working_dic_exists
        from .services import working_dic_path_for_user_id

        source_dic = Path(getattr(dj_settings, "HUNSPELL_DIC_SOURCE_PATH"))
        working_dic = working_dic_path_for_user_id(int(user_id))
        ensure_working_dic_exists(source_dic, working_dic)
    except Exception:
        return


class ReviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'review'

    def ready(self) -> None:
        # Ensure per-user working dictionaries exist on account creation.
        try:
            from django.contrib.auth import get_user_model
            from django.db.models.signals import post_save

            User = get_user_model()

            def _on_user_saved(sender, instance, created, **kwargs):
                if not created:
                    return
                # Avoid slowing down the admin save; copy happens in background.
                threading.Thread(
                    target=_ensure_user_working_dic_exists,
                    args=(instance.id,),
                    name=f"init-user-dic-{instance.id}",
                    daemon=True,
                ).start()

            post_save.connect(_on_user_saved, sender=User, dispatch_uid="review.init_user_working_dic")
        except Exception:
            # Never fail app startup due to signal registration.
            pass

        # Warm .aff caches so the first reviewer doesn't pay the full parse/index cost.
        if not getattr(settings, "WARM_AFF_CACHE_ON_STARTUP", True):
            return

        # In Django runserver, avoid doing this in the autoreloader parent process.
        if settings.DEBUG and os.environ.get("RUN_MAIN") != "true":
            return

        def _warm() -> None:
            try:
                from .hunspell import _aff_signature, _detect_flag_mode_cached

                aff_path = Path(getattr(settings, "HUNSPELL_AFF_PATH"))
                sig = _aff_signature(aff_path)
                t0 = time.perf_counter()
                _detect_flag_mode_cached(*sig)
                _ = time.perf_counter() - t0
            except Exception:
                # Best-effort only; never break app startup.
                return

        threading.Thread(target=_warm, name="warm-aff-cache", daemon=True).start()
