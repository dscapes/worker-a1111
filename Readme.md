# API a1111

```json
{
    "input": {
        "port": 17860,
        "method": "post",
        "path": "/sdapi/v1/txt2img",
        "body": {
            "prompt": "a photo of a cat",
        }
    }
}
```
Port API automatic1111 (can be found in logs when starting)

# Download

```json
{
    "input": {
        "method": "DOWNLOAD",
        "url": "https://civitai.com/api/v1/models/123456",
        "save_dir": "/loras",
        "save_filename": "model.safetensors"
    }
}
```

# Upload

```json
{
    "input": {
        "method": "UPLOAD",
        "files": ["/path/to/file1.txt", "/path/to/file2.jpg"],
        "target_url": "https://api.example.com/upload",
        "auth_token": "your-auth-token"
    }
}
```

```json
{
    "uploaded": [
        {"path": "/path/to/file1.txt", "response": {...}},
        {"path": "/path/to/file2.jpg", "response": {...}}
    ],
    "failed": [
        {"path": "/path/to/file3.png", "error": "File not found"}
    ]
}
```