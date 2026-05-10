from __future__ import annotations

import argparse
import hashlib
import mimetypes
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

TOOL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]
DEFAULT_GAMES_ROOT = REPO_ROOT / "games"


@dataclass(frozen=True)
class UploadPlan:
    source: Path
    bucket: str
    key_root: str
    destination_name: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy a local game directory into a staging area and upload it to a Cloudflare R2 destination."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Source game directory or file path. Relative paths resolve from the repository root and then games/.",
    )
    parser.add_argument(
        "--games-root",
        default=str(DEFAULT_GAMES_ROOT),
        help="Default root for game-relative paths. Defaults to the repository games/ directory.",
    )
    parser.add_argument(
        "--bucket",
        default=os.environ.get("R2_BUCKET"),
        help="R2 bucket name. Defaults to R2_BUCKET.",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Destination prefix inside the bucket, e.g. published/2026.",
    )
    parser.add_argument(
        "--destination-name",
        help="Override the uploaded top-level folder/file name. Defaults to the source name.",
    )
    parser.add_argument(
        "--endpoint-url",
        default=os.environ.get("R2_ENDPOINT_URL"),
        help="Explicit S3-compatible endpoint URL. If omitted, it is derived from R2_ACCOUNT_ID.",
    )
    parser.add_argument(
        "--content-type",
        help="Optional fixed content type for every uploaded file. Defaults to mime-type inference.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the upload plan without copying or uploading files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow uploading over an existing destination prefix.",
    )
    return parser


def normalize_prefix(prefix: str) -> str:
    return prefix.strip("/")


def join_key(*parts: str) -> str:
    cleaned = [part.strip("/") for part in parts if part and part.strip("/")]
    return "/".join(cleaned)


def resolve_source_path(raw_source: str, games_root: Path) -> Path:
    source = Path(raw_source)
    candidates: list[Path] = []
    if source.is_absolute():
        candidates.append(source)
    else:
        candidates.append((REPO_ROOT / source).resolve())
        candidates.append((games_root / source).resolve())
    for candidate in candidates:
        if candidate.exists():
            return candidate
    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Source path does not exist. Checked: {searched}")


def build_plan(args: argparse.Namespace) -> UploadPlan:
    games_root = Path(args.games_root).resolve()
    source = resolve_source_path(args.source, games_root)
    destination_name = args.destination_name or source.name
    key_root = join_key(normalize_prefix(args.prefix), destination_name)
    if not args.bucket:
        raise ValueError("Bucket is required. Pass --bucket or set R2_BUCKET.")
    if not key_root:
        raise ValueError("Destination key cannot be empty.")
    return UploadPlan(
        source=source,
        bucket=args.bucket,
        key_root=key_root,
        destination_name=destination_name,
    )


def build_endpoint_url(account_id: str | None, explicit_url: str | None) -> str:
    if explicit_url:
        return explicit_url
    if not account_id:
        raise ValueError("Provide --endpoint-url or set R2_ACCOUNT_ID.")
    return f"https://{account_id}.r2.cloudflarestorage.com"


def build_r2_client(endpoint_url: str) -> Any:
    try:
        import boto3
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "boto3 is required for uploads. Install repository dependencies with `pip install -r requirements.txt`."
        ) from exc

    access_key_id = os.environ.get("R2_ACCESS_KEY_ID")
    secret_access_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    if not access_key_id or not secret_access_key:
        raise ValueError("Set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY.")
    session = boto3.session.Session()
    return session.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name="auto",
    )


def iter_files(root: Path) -> Iterator[Path]:
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def stage_source(source: Path) -> tuple[Path, Path]:
    staging_root = Path(tempfile.mkdtemp(prefix="game-uploader-r2-"))
    staged_path = staging_root / source.name
    if source.is_dir():
        shutil.copytree(source, staged_path)
    else:
        staged_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, staged_path)
    return staging_root, staged_path


def destination_exists(client: Any, bucket: str, destination_key_root: str) -> bool:
    probe_prefix = destination_key_root.rstrip("/") + "/"
    response = client.list_objects_v2(Bucket=bucket, Prefix=probe_prefix, MaxKeys=1)
    if response.get("KeyCount", 0):
        return True
    try:
        client.head_object(Bucket=bucket, Key=destination_key_root)
        return True
    except Exception as exc:
        error_code = getattr(exc, "response", {}).get("Error", {}).get("Code")
        if error_code in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise


def guess_content_type(path: Path, override: str | None) -> str | None:
    if override:
        return override
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed


def sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_object_key(file_path: Path, staged_path: Path, key_root: str) -> str:
    if staged_path.is_file():
        return key_root
    relative_path = file_path.relative_to(staged_path)
    return join_key(key_root, relative_path.as_posix())


def upload_file(
    client: Any,
    *,
    bucket: str,
    local_path: Path,
    object_key: str,
    content_type: str | None,
) -> None:
    extra_args: dict[str, str] = {}
    if content_type:
        extra_args["ContentType"] = content_type
    upload_kwargs: dict[str, Any] = {
        "Filename": str(local_path),
        "Bucket": bucket,
        "Key": object_key,
    }
    if extra_args:
        upload_kwargs["ExtraArgs"] = extra_args
    client.upload_file(**upload_kwargs)


def print_plan(plan: UploadPlan) -> None:
    print(f"Resolved source: {plan.source}")
    print(f"Destination bucket: {plan.bucket}")
    print(f"Destination key root: {plan.key_root}")


def run_upload(args: argparse.Namespace) -> int:
    plan = build_plan(args)
    print_plan(plan)

    if args.dry_run:
        for file_path in iter_files(plan.source):
            object_key = plan.key_root if plan.source.is_file() else join_key(
                plan.key_root, file_path.relative_to(plan.source).as_posix()
            )
            print(f"DRY RUN upload {file_path} -> s3://{plan.bucket}/{object_key}")
        return 0

    endpoint_url = build_endpoint_url(os.environ.get("R2_ACCOUNT_ID"), args.endpoint_url)
    client = build_r2_client(endpoint_url)

    if destination_exists(client, plan.bucket, plan.key_root) and not args.force:
        raise SystemExit(
            f"Destination already exists at s3://{plan.bucket}/{plan.key_root}. Re-run with --force to upload over it."
        )

    staging_root, staged_path = stage_source(plan.source)
    uploaded_count = 0

    try:
        for file_path in iter_files(staged_path):
            object_key = build_object_key(file_path, staged_path, plan.key_root)
            content_type = guess_content_type(file_path, args.content_type)
            checksum = sha256_for_file(file_path)
            print(f"Uploading {file_path} -> s3://{plan.bucket}/{object_key} sha256={checksum}")
            upload_file(
                client,
                bucket=plan.bucket,
                local_path=file_path,
                object_key=object_key,
                content_type=content_type,
            )
            uploaded_count += 1
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)

    print(f"Upload complete. Uploaded {uploaded_count} file(s) to s3://{plan.bucket}/{plan.key_root}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_upload(args)