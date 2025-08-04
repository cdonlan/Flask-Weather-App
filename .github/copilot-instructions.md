# Custom Instructions for GitHub Copilot (Python)

- Use idiomatic Python 3.10+ syntax, including structural pattern matching when helpful.
- Favor list comprehensions and `enumerate` over manual index iteration.
- When creating CLI tools, prefer the `argparse` module over manual `sys.argv` parsing.
- For async code, use `asyncio.run()` and `async/await`, and avoid legacy event loop code.
- Follow PEP 8 naming conventions. Use `snake_case` for functions and variables, and `PascalCase` for classes.
- Use type hints throughout (`def foo(bar: int) -> str:`).
- Write docstrings in Google style format.
