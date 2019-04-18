from .base import WebHookHandlers
from .cci_handler import trigger_dependent_cci, clear_records_when_ref_deleted
from .dingding_handler import send_dingding_message_on_updated_failed_pipeline
from .review_handler import update_release_status


# cci handler
WebHookHandlers.add_handler('Pipeline Hook', trigger_dependent_cci)
WebHookHandlers.add_handler('Tag Push Hook', clear_records_when_ref_deleted)
WebHookHandlers.add_handler('Push Hook', clear_records_when_ref_deleted)

# dingding handler
WebHookHandlers.add_handler('Pipeline Hook', send_dingding_message_on_updated_failed_pipeline)

# review handler
WebHookHandlers.add_handler('Merge Request Hook', update_release_status)
