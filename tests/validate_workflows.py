from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
UNIFIED = ROOT / ".github/workflows/unified-build.yml"
RELEASE_DOCKERFILE = ROOT / "alpine/Dockerfile"
DEBUG_DOCKERFILE = ROOT / "alpine/Dockerfile-debug"
LEGACY_FILES = [
    ROOT / ".github/workflows/build.yml",
    ROOT / ".github/workflows/build-32bit.yml",
    ROOT / ".github/workflows/build-amd64.yml",
    ROOT / ".github/workflows/build-amd64-debug.yml",
]


def require(content: str, needle: str, message: str) -> None:
    if needle not in content:
        raise AssertionError(message)


def forbid_path(path: Path, message: str) -> None:
    if path.exists():
        raise AssertionError(message)


def main() -> None:
    if not UNIFIED.exists():
        raise AssertionError("缺少统一入口 workflow: .github/workflows/unified-build.yml")

    content = UNIFIED.read_text()
    release_dockerfile = RELEASE_DOCKERFILE.read_text()
    debug_dockerfile = DEBUG_DOCKERFILE.read_text()

    require(content, "workflow_dispatch:", "统一 workflow 必须支持手工触发")
    require(content, "schedule:", "统一 workflow 必须保留定时触发")
    require(content, "resume_round:", "统一 workflow 必须显式定义 resume_round 输入")
    require(content, "resume_targets:", "统一 workflow 必须显式定义 resume_targets 输入")
    require(content, "resume_state_ref:", "统一 workflow 必须显式定义 resume_state_ref 输入")
    require(content, "prepare:", "统一 workflow 必须包含 prepare job")
    require(content, "build-release-64:", "统一 workflow 必须包含 build-release-64 job")
    require(content, "build-release-32:", "统一 workflow 必须包含 build-release-32 job")
    require(content, "build-debug-64:", "统一 workflow 必须包含 build-debug-64 job")
    require(content, "build-debug-32:", "统一 workflow 必须包含 build-debug-32 job")
    require(content, "publish:", "统一 workflow 必须包含 publish job")
    require(content, "handoff-or-fail:", "统一 workflow 必须包含 handoff-or-fail job")
    require(content, "latest-debug", "统一 workflow 必须保留 debug 汇总 tag")
    require(content, "--file ./alpine/Dockerfile \\", "release family 必须使用 release Dockerfile")
    require(content, "--file ./alpine/Dockerfile-debug \\", "debug family 必须使用 debug Dockerfile")
    require(release_dockerfile, "-DCMAKE_BUILD_TYPE=Release", "release Dockerfile 必须构建 Release")
    require(release_dockerfile, '-DCMAKE_CXX_FLAGS_RELEASE="-O2 -DNDEBUG"', "release Dockerfile 必须限制优化级别以满足 hosted runner 时限")
    require(release_dockerfile, "-G Ninja", "release Dockerfile 必须使用 Ninja 降低构建开销")
    require(debug_dockerfile, "-DCMAKE_BUILD_TYPE=Debug", "debug Dockerfile 必须构建 Debug")

    for path in LEGACY_FILES:
        forbid_path(path, f"旧 workflow 必须退役: {path.name}")


if __name__ == "__main__":
    main()