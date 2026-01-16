#!/usr/bin/env python3
"""
Script to upload NER project to Hugging Face Spaces (Docker-based)
"""
import os
import glob
from huggingface_hub import HfApi, create_repo

# Load token from .env
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
SPACE_NAME = "turkish-extended-ner"
REPO_ID = f"WildGenie/{SPACE_NAME}"

def main():
    api = HfApi(token=HF_TOKEN)

    # Create Space if not exists
    try:
        create_repo(
            repo_id=REPO_ID,
            repo_type="space",
            space_sdk="docker",  # Changed to docker
            token=HF_TOKEN,
            exist_ok=True
        )
        print(f"✅ Space created/verified: {REPO_ID}")
    except Exception as e:
        print(f"⚠️ Repo creation: {e}")

    # Files and folders to upload
    files_to_upload = [
        ("Demo.py", "Demo.py"),
        ("Dockerfile", "Dockerfile"),
        (".dockerignore", ".dockerignore"),
        ("HF_README.md", "README.md"),
        ("requirements.txt", "requirements.txt"),

        # Source code
        ("src/__init__.py", "src/__init__.py"),
        ("src/features.py", "src/features.py"),
        ("src/preprocessing.py", "src/preprocessing.py"),
        ("src/nuve_bridge.py", "src/nuve_bridge.py"),
        ("src/models/__init__.py", "src/models/__init__.py"),
        ("src/models/crf_model.py", "src/models/crf_model.py"),

        # Models
        ("models/crf_gold_best.pkl", "models/crf_gold_best.pkl"),
        ("models/crf_gold_no_emb.pkl", "models/crf_gold_no_emb.pkl"),
        ("models/crf_gold_gaz_only.pkl", "models/crf_gold_gaz_only.pkl"),

        # Gazetteers
        ("gazetteers/kisiler.txt", "gazetteers/kisiler.txt"),
        ("gazetteers/yerler.txt", "gazetteers/yerler.txt"),
        ("gazetteers/kurumlar.txt", "gazetteers/kurumlar.txt"),
        ("gazetteers/sirketler.txt", "gazetteers/sirketler.txt"),
        ("gazetteers/topluluklar.txt", "gazetteers/topluluklar.txt"),
        ("gazetteers/film_muzik.txt", "gazetteers/film_muzik.txt"),

        # Nuve Wrapper
        ("nuve_wrapper/Program.cs", "nuve_wrapper/Program.cs"),
        ("nuve_wrapper/nuve_wrapper.csproj", "nuve_wrapper/nuve_wrapper.csproj"),

        # Documentation
        ("docs/Akademik_Makale.md", "docs/Akademik_Makale.md"),
    ]

    # Add all files from pages directory
    if os.path.exists("pages"):
        for f in glob.glob("pages/*.py"):
            files_to_upload.append((f, f))

    # Add all result files for dashboard
    if os.path.exists("results/experiments"):
        for f in glob.glob("results/experiments/*.json"):
            # Only upload what's needed to avoid too many files
            files_to_upload.append((f, f))

    print(f"\n📤 Uploading files to {REPO_ID}...")

    for local_path, repo_path in files_to_upload:
        if os.path.exists(local_path):
            try:
                # Use upload_file for individual files
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=repo_path,
                    repo_id=REPO_ID,
                    repo_type="space",
                    token=HF_TOKEN
                )
                print(f"  ✓ {local_path} → {repo_path}")
            except Exception as e:
                # If it fails due to no changes, that's fine
                if "No files have been modified" in str(e):
                    print(f"  - {local_path} (No changes)")
                else:
                    print(f"  ✗ {local_path}: {e}")
        else:
            print(f"  ⚠️ Not found: {local_path}")

    print(f"\n🎉 Done! Visit: https://huggingface.co/spaces/{REPO_ID}")

if __name__ == "__main__":
    main()
