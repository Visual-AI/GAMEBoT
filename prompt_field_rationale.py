"""Field-rationale prompt variants for GAMEBoT prompts.

The final action sections are intentionally preserved so existing parsers such as
`Chosen Move`, `Chosen Action`, and `Proposal` keep working.
"""

FIELD_REGISTERS = {
    "tictactoe": [
        "board_state",
        "legal_empty_squares",
        "own_immediate_winning_moves",
        "opponent_immediate_winning_moves",
        "center_corner_edge_value",
        "candidate_move_values",
    ],
    "connect4": [
        "board_state",
        "legal_drop_columns",
        "own_immediate_winning_moves",
        "opponent_immediate_winning_moves",
        "center_column_control",
        "multi_threat_creation",
        "candidate_move_values",
    ],
    "othello": [
        "board_state",
        "legal_moves",
        "corner_control",
        "edge_control",
        "piece_stability",
        "frontier_discs",
        "wedge_opportunities",
        "mobility",
        "candidate_move_values",
    ],
    "checkers": [
        "board_state",
        "legal_moves",
        "mandatory_capture_options",
        "king_promotion_moves",
        "worthless_die_risk",
        "two_for_one_shots",
        "piece_safety_and_material",
        "candidate_move_values",
    ],
    "pong": [
        "ball_direction",
        "ball_trajectory_to_paddle",
        "own_paddle_position",
        "opponent_paddle_position",
        "wall_rebound_prediction",
        "intercept_position_value",
        "candidate_action_values",
    ],
    "surround": [
        "current_position",
        "adjacent_cell_values",
        "valid_move_set",
        "future_empty_space",
        "self_trap_risk",
        "opponent_trap_opportunity",
        "candidate_action_values",
    ],
    "negotiate": [
        "pool_and_private_values",
        "latest_proposal_value",
        "proposal_history_trend",
        "opponent_value_beliefs",
        "round_end_risk",
        "proposal_validity",
        "candidate_proposal_values",
    ],
    "texas": [
        "private_cards",
        "community_cards",
        "available_betting_actions",
        "hand_strength_or_equity",
        "pot_commitment",
        "opponent_betting_pressure",
        "candidate_action_values",
    ],
}

FINAL_SECTION_MARKERS = [
    "**[Action]**",
    "3. **Chosen Move**",
    "4. **Chosen Move**",
    "5. **Chosen Action**",
    "3. **Chosen Action**",
    "5. **Proposal**",
]

PROCESS_MARKER = "Follow the thinking process:"


def normalize_prompt_type(prompt_type):
    if prompt_type in {None, "", "cot", "naive", "no", "original"}:
        return "original"
    if prompt_type in {"field_aux", "field_only"}:
        return prompt_type
    raise ValueError(
        f"Unsupported prompt_type={prompt_type!r}; use original, field_aux, or field_only."
    )


def _field_register_block(game_name):
    fields = FIELD_REGISTERS[game_name]
    return "\n".join(f"- {field}" for field in fields)


def _field_section(game_name):
    return f"""

**Decision Fields**
Use the Field Register only as a compact way to explain the reasoning behind your chosen move or action.
Do not treat the fields as additional game rules or extra available actions.

Field Register:
{_field_register_block(game_name)}

Field Selection Rule:
Select 2 to 4 fields from the Field Register.
Prefer the smallest sufficient set of fields for the decision.
Use only fields that directly affect the chosen move or action; do not include fields that are only generally relevant.
Use 4 fields only when multiple competing factors materially affect the decision.

Before the final chosen move/action section, include:
{{
  "used_fields": [
    "2 to 4 field names copied exactly from the Field Register"
  ],
  "field_analysis": [
    {{
      "field": "one exact field name from used_fields",
      "value": "short phrase explaining why that field supports the selected move or action"
    }}
  ]
}}

Rules:
- used_fields must contain 2 to 4 field names copied exactly from the Field Register.
- field_analysis must contain exactly one object per used field, in the same order.
- Keep each field_analysis.value short.
"""


def _find_final_marker(prompt):
    positions = [
        (prompt.find(marker), marker)
        for marker in FINAL_SECTION_MARKERS
        if prompt.find(marker) != -1
    ]
    if not positions:
        return -1, None
    return min(positions, key=lambda item: item[0])


def _insert_before_final_section(prompt, section):
    idx, _ = _find_final_marker(prompt)
    if idx == -1:
        return prompt.rstrip() + section
    return prompt[:idx].rstrip() + section + "\n\n" + prompt[idx:]


def _replace_process_with_field_section(prompt, section):
    process_idx = prompt.find(PROCESS_MARKER)
    final_idx, _ = _find_final_marker(prompt)
    if process_idx == -1 or final_idx == -1 or final_idx <= process_idx:
        return _insert_before_final_section(prompt, section)
    prefix = prompt[: process_idx + len(PROCESS_MARKER)].rstrip()
    final_section = prompt[final_idx:].lstrip()
    return prefix + section + "\n\n" + final_section


def build_gamebot_prompt(game_name, base_prompt, prompt_type="original", role=None):
    prompt_type = normalize_prompt_type(prompt_type)
    if prompt_type == "original":
        return base_prompt
    if game_name not in FIELD_REGISTERS:
        raise ValueError(f"No Field Register configured for game_name={game_name!r}")
    section = _field_section(game_name)
    if role:
        section = section.replace("**Decision Fields**", f"**Decision Fields ({role})**", 1)
    if prompt_type == "field_aux":
        return _insert_before_final_section(base_prompt, section)
    return _replace_process_with_field_section(base_prompt, section)
