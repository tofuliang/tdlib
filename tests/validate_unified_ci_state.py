from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
UNIFIED = ROOT / ".github/workflows/unified-build.yml"


def require(content: str, needle: str, message: str) -> None:
    if needle not in content:
        raise AssertionError(message)


def main() -> None:
    content = UNIFIED.read_text()

    require(content, 'resume_round', '统一 workflow 必须显式使用 resume_round')
    require(content, 'resume_state_ref', '统一 workflow 必须显式使用 resume_state_ref')
    require(content, 'needs_handoff', '统一 workflow 必须显式记录 needs_handoff 状态')
    require(content, 'last_completed_stage', '统一 workflow 必须显式记录 last_completed_stage')
    require(content, 'remaining_stages', '统一 workflow 必须显式记录 remaining_stages')
    require(content, 'status', '统一 workflow 必须显式记录 family 状态')
    require(content, 'handoff-or-fail:', '统一 workflow 必须包含统一续跑协调 job')
    require(content, 'resume_round < 2', '统一 workflow 必须限制自动续跑不超过两轮')
    require(content, 'actions/upload-artifact', '统一 workflow 必须上传状态 artifact')
    require(content, 'actions/download-artifact', '统一 workflow 必须支持恢复上一轮状态 artifact')
    require(content, 'needs: [prepare, build-release-64, build-release-32, build-debug-64, build-debug-32]', 'publish job 必须显式依赖 prepare 和四个 build family')
    require(content, 'run-id: ${{ needs.prepare.outputs.resume_state_ref }}', 'resume_state_ref 必须明确作为上一轮 run-id 使用')
    if content.count('github-token: ${{ secrets.GITHUB_TOKEN }}') != 4:
        raise AssertionError('四个 family 跨 Run 下载状态 artifact 时都必须显式传递 GitHub token')
    if content.count('repository: ${{ github.repository }}') != 4:
        raise AssertionError('四个 family 跨 Run 下载状态 artifact 时都必须显式指定当前仓库')
    require(content, 'contains(needs.prepare.outputs.resume_targets', '续跑时必须基于 resume_targets 选择要执行的 family job')
    require(content, 'gh workflow run', 'handoff-or-fail 必须真正触发下一轮 workflow，而不是仅打印提示')
    require(content, '--field resume_round=', 'handoff 触发下一轮时必须传递新的 resume_round')
    require(content, '--field resume_targets=', 'handoff 触发下一轮时必须传递未完成 family 的 resume_targets')
    require(content, '--field resume_state_ref=', 'handoff 触发下一轮时必须传递当前 run-id 作为 resume_state_ref')

    if content.count('if [ "$status" = "handoff" ]; then\n              status="running"') != 4:
        raise AssertionError('四个 build family 都必须将恢复的 handoff 状态转回 running')
    if content.count('timeout-minutes: 330') != 4:
        raise AssertionError('四个 build family 都必须在 hosted runner 六小时硬上限前结束构建步骤')
    if content.count('continue-on-error: true') != 4:
        raise AssertionError('构建步骤超时后必须继续上传 family state')
    if content.count('- name: Upload family state\n        if: ${{ always() }}') != 4:
        raise AssertionError('四个 family state artifact 都必须在失败或超时时上传')
    if content.count('check_timed_handoff "$last_completed_stage" "$remaining_stages"') != 8:
        raise AssertionError('每个架构开始前都必须使用恢复后的阶段状态判断 handoff')
    require(content, 'handoff|running)', 'handoff 协调器必须将超时后仍为 running 的 family 加入续跑目标')
    if content.count('*release_64.json) incomplete_targets+=("release-64") ;;') != 1:
        raise AssertionError('release-64 的 running/handoff 状态必须映射到精确续跑目标')
    if content.count('*release_32.json) incomplete_targets+=("release-32") ;;') != 1:
        raise AssertionError('release-32 的 running/handoff 状态必须映射到精确续跑目标')
    if content.count('*debug_64.json) incomplete_targets+=("debug-64") ;;') != 1:
        raise AssertionError('debug-64 的 running/handoff 状态必须映射到精确续跑目标')
    if content.count('*debug_32.json) incomplete_targets+=("debug-32") ;;') != 1:
        raise AssertionError('debug-32 的 running/handoff 状态必须映射到精确续跑目标')

    stages = [
        'release-64-amd64',
        'release-64-arm64',
        'release-32-386',
        'release-32-armv7',
        'debug-64-amd64',
        'debug-64-arm64',
        'debug-32-386',
        'debug-32-armv7',
    ]
    for stage in stages:
        require(
            content,
            f'if jq -e --arg stage "{stage}" \'index($stage) != null\' <<< "$remaining_stages" > /dev/null; then',
            f'续跑必须只执行 remaining_stages 中的阶段: {stage}',
        )


if __name__ == '__main__':
    main()
