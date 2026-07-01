FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
COPY sample_data ./sample_data

RUN pip install --no-cache-dir ".[mcp]"

ENV FILE_MEMORY_DATA_DIR=/app/sample_data
ENV ACL_PATH=/app/config/acl.json

CMD ["python", "-m", "mcp_file_memory_demo.server"]
