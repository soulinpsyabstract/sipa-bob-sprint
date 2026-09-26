"""Maps a raw Bob tool_use event to a sipa-trace ActionProfile.

Deliberately generic: this reads what KIND of tool Bob called (file write,
shell exec, network fetch, etc.) and what it touched — never the specific
domain of the task Bob was given. Same classifier works whether Bob is
reviewing a payments app, a reservation system, or anything else — it
classifies capability, not intent.
"""
from __future__ import annotations

from sipa_trace import ActionProfile

# Tool names that write/modify the filesystem, by convention across coding
# agents (Bob, Claude Code, etc all use broadly this vocabulary).
_WRITE_TOOLS = {"write_file", "edit_file", "apply_patch", "create_file", "str_replace"}
_DELETE_TOOLS = {"delete_file", "remove_file", "rm"}
_EXEC_TOOLS = {"execute_command", "run_command", "shell", "bash", "terminal"}
_NETWORK_TOOLS = {"web_search", "web_fetch", "http_request", "curl"}
_CREDENTIAL_HINTS = ("token", "key", "secret", "password", "credential", "auth")

# Shell command substrings that mean "this exec touched the filesystem
# irreversibly" even though the tool itself is generic "run a command".
_DESTRUCTIVE_SHELL_HINTS = ("rm -rf", "rm -f", "git reset --hard", "git clean -fd",
                            "> /dev/", "drop table", "truncate table")


def _params_mention_credentials(params: dict) -> bool:
    blob = str(params).lower()
    return any(hint in blob for hint in _CREDENTIAL_HINTS)


def _shell_command_is_destructive(params: dict) -> bool:
    cmd = str(params.get("command", params.get("cmd", ""))).lower()
    return any(hint in cmd for hint in _DESTRUCTIVE_SHELL_HINTS)


def classify_tool_call(tool_name: str, parameters: dict) -> ActionProfile:
    """Build a generic ActionProfile from a Bob tool_use event.

    Conservative by design: anything not recognised falls through to a
    read-only, reversible, no-network profile (RiskClass.NONE) rather than
    silently escalating — an unknown tool should show up as NONE/LOW, not
    get mis-classified as safe-by-default HIGH-risk behaviour, or the
    reverse.
    """
    name = (tool_name or "").lower()

    is_write = name in _WRITE_TOOLS
    is_delete = name in _DELETE_TOOLS
    is_exec = name in _EXEC_TOOLS
    is_network = name in _NETWORK_TOOLS
    touches_credentials = _params_mention_credentials(parameters)

    reversible = True
    if is_delete:
        reversible = False
    if is_exec and _shell_command_is_destructive(parameters):
        is_delete = True
        reversible = False

    return ActionProfile(
        touches_credentials=touches_credentials,
        external_network_call=is_network or is_exec,  # exec can shell out to network too
        writes_data=is_write or is_exec,
        deletes_data=is_delete,
        record_count=1,
        reversible=reversible,
        model_invoked=False,  # the tool call itself isn't the model call; Bob's own inference is
    )
