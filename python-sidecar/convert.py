#!/usr/bin/env python3
"""
MarkIt-Desktop conversion sidecar.
Reads JSON from stdin, writes line-delimited JSON events to stdout.

Input format:
{
  "files": ["/path/to/file1.pdf", "/path/to/file2.docx"],
  "output_dir": "/optional/output/directory",
  "use_ocr": false,
  "extract_images": true
}

Output format (line-delimited JSON):
{"event": "started", "file": "/path/to/file1.pdf", "index": 0, "total": 2}
{"event": "finished", "file": "/path/to/file1.pdf", "index": 0, "markdown": "# ...", "output_path": "..."}
{"event": "error", "file": "/path/to/file1.pdf", "index": 0, "error": "Error message"}
{"event": "complete", "total": 2, "success": 1, "failed": 1}
"""

import sys
import json
import os
from pathlib import Path

try:
    from markitdown import MarkItDown
except (ImportError, AttributeError):
    print(json.dumps({
        "event": "error",
        "error": "markitdown package not installed or incomplete"
    }), flush=True)
    sys.exit(1)


def emit_event(event: dict):
    """Write a JSON event to stdout and flush."""
    print(json.dumps(event, ensure_ascii=False), flush=True)


def convert_files(input_data: dict):
    """Process a list of files and emit events."""
    files = input_data.get("files", [])
    output_dir = input_data.get("output_dir", "")
    use_ocr = input_data.get("use_ocr", False)
    extract_images = input_data.get("extract_images", True)

    if not files:
        emit_event({"event": "error", "error": "No files provided"})
        return

    # Initialize converter
    try:
        converter = MarkItDown(
            enable_builtins=True,
            use_ocr=use_ocr,
            extract_images=extract_images
        )
    except Exception as e:
        emit_event({"event": "error", "error": f"Failed to initialize converter: {str(e)}"})
        return

    total = len(files)
    success_count = 0
    failed_count = 0

    for index, file_path in enumerate(files):
        emit_event({
            "event": "started",
            "file": file_path,
            "index": index,
            "total": total
        })

        try:
            # Convert the file
            result = converter.convert(file_path)
            markdown = result.text_content

            # Optionally save to output directory
            output_path = ""
            if output_dir:
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    source_name = Path(file_path).stem
                    output_path = os.path.join(output_dir, f"{source_name}.md")
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(markdown)
                except Exception as e:
                    emit_event({
                        "event": "warning",
                        "file": file_path,
                        "index": index,
                        "warning": f"Failed to save output: {str(e)}"
                    })
                    output_path = ""

            emit_event({
                "event": "finished",
                "file": file_path,
                "index": index,
                "markdown": markdown,
                "output_path": output_path
            })
            success_count += 1

        except Exception as e:
            emit_event({
                "event": "error",
                "file": file_path,
                "index": index,
                "error": str(e)
            })
            failed_count += 1

    emit_event({
        "event": "complete",
        "total": total,
        "success": success_count,
        "failed": failed_count
    })


def main():
    """Main entry point."""
    try:
        # Read JSON from stdin
        input_text = sys.stdin.read()
        if not input_text.strip():
            emit_event({"event": "error", "error": "No input provided"})
            sys.exit(1)

        input_data = json.loads(input_text)

        # Validate input
        if not isinstance(input_data, dict):
            emit_event({"event": "error", "error": "Input must be a JSON object"})
            sys.exit(1)

        # Process files
        convert_files(input_data)

    except json.JSONDecodeError as e:
        emit_event({"event": "error", "error": f"Invalid JSON input: {str(e)}"})
        sys.exit(1)
    except Exception as e:
        emit_event({"event": "error", "error": f"Unexpected error: {str(e)}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
