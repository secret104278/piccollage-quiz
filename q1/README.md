
## Develop
Enter vscode devcontainer

```sh
python tools/gen_image_vectors.py
uvicorn app.main:app --reload
```

## Testing

```sh
pytest
```

## TODO
- external dependecies `clip.load`, currently we use implicit cache
