#!/bin/bash

alembic upgrade head
uvicorn src.main:app --port 8080 --host 0.0.0.0