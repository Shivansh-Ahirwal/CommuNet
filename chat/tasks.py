from celery import shared_task
from .models import BaseMongoModel, Message
import datetime
import uuid


@shared_task(name="chat.tasks.upload_file_to_gridfs")
def upload_file_to_gridfs(file_data_str,
                          filename,
                          content_type,
                          sender_id,
                          chat_id,
                          message_id,
                          text=None):
    from .views import broadcast_file_message
    try:
        fs = BaseMongoModel.get_gridfs_instance()

        file_id = fs.put(file_data_str,
                         filename=filename,
                         content_type=content_type)

        if content_type.startswith("image"):
            content_type = "image"
        else:
            content_type = "video"

        Message().update(filter={"_id": message_id}, update={
            "chat_id": chat_id,
            "sender_id": int(sender_id),
            "file_type": content_type,
            "file_id": str(file_id),
            "timestamp": datetime.datetime.utcnow(),
            "text": text
        })

        broadcast_file_message(chat_id, sender_id, str(file_id), content_type, text)

        return str(file_id)

    except Exception as e:
        print(f"[Celery Task Error] Failed to upload file: {e}")
        return None
