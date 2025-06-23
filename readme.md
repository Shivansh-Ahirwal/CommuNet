# 🧠 Communet — Real-Time Chat Application with File Sharing and Background Processing

## 🚀 Project Overview

Communet is a full-stack, real-time chat application currently under active development. It supports both text and media messaging (images and videos) using WebSockets and GridFS for storage, with Celery handling background processing to ensure seamless user experience. This project combines the power of **Django**, **Channels**, **MongoDB + GridFS**, **Celery**, and **RabbitMQ** to create a scalable and responsive chat platform.

---

## 🛠️ Tech Stack

* **Backend:** Django, Django Channels, MongoDB, GridFS, Celery, RabbitMQ
* **Frontend:** HTML, CSS, JavaScript (jQuery for DOM & AJAX handling)
* **Async Processing:** Celery with RabbitMQ as broker
* **Database:** MongoDB (with GridFS for media file storage)
* **File Handling:** Asynchronous uploads via Celery tasks

---

## 📈 Project Journey So Far

### ✅ Phase 1: Initial Setup

* Set up Django project and apps for chat functionality.
* Configured MongoDB as primary data store for chat messages.
* Designed basic UI for chat layout (inspired by WhatsApp aesthetic).

### ✅ Phase 2: WebSocket Integration

* Implemented Django Channels for real-time messaging using WebSocket protocol.
* Enabled dynamic message rendering based on sender identity (incoming/outgoing).
* Tested real-time text messaging with multiple users across different sessions.

### ✅ Phase 3: Media Messaging (Image/Video Uploads)

* Added frontend input for uploading images and videos.
* Used `FileReader` and `base64` to send files through WebSocket.
* Setup MongoDB GridFS for handling large file storage efficiently.
* Wrote Celery task (`upload_file_to_gridfs`) to asynchronously store files in GridFS.

### ✅ Phase 4: Background Task Management

* Installed and configured **RabbitMQ** on WSL and integrated it with **Celery** running on Windows.
* Debugged issues with Windows `billiard` process pool — resolved using custom Celery solo pool or adjusting concurrency settings.
* Verified file upload task execution and real-time rendering via Celery log monitoring.

### ✅ Phase 5: Message Persistence

* Added MongoDB model abstraction to persist messages with or without media.
* Created a dedicated message ID (UUID) to track related file/message combinations.
* Ensured real-time file delivery through `broadcast_file_message` on successful upload.

### 🔧 Challenges Faced

* Celery Windows compatibility: Needed multiple debugging sessions for multiprocessing issues.
* WebSocket and File Handling: Ensured base64 decoding and secure file handling.
* File visibility: Delayed image rendering in chat unless page refreshed — identified caching or async delay in file broadcast.
* Planned feature (in progress): Display blurred media placeholders until the user clicks/downloads the full media.

---

## 🚧 Upcoming Milestones

* ✅ Fix double-message rendering for media-only uploads.
* ⏳ Implement image download-before-render feature (media lock).
* ⏳ Add authentication, user groups, and private/public chats.
* ⏳ Enhance frontend experience with Vue/React (optional).
* ⏳ Dockerize the full app and deploy to a production-ready server.

---

## 📎 Project Status

**Current Phase:** Feature Refinement + UX Optimization
**Completion:** \~70%
**Team:** Solo Developer
**Tech Goal:** Build an end-to-end production-ready real-time communication system.
