from datetime import datetime

from simulation.persona.common import PersonaIdentity
from simulation.utils import ModelWandbWrapper
from pathfinder import assistant, system, user

from .utils import (
    consider_identity_persona_prompt,
    conversation_to_string_with_dash,
    revenge_identity_persona_prompt,
    get_sytem_prompt,
    list_to_comma_string,
    list_to_string_with_dash,
    location_time_info,
    memory_prompt,
    reasoning_steps_prompt,
)

revenge_jack_flag = True
revenge_others_flag = True

def prompt_action_choose_amount_of_fish_to_catch(
    model: ModelWandbWrapper,
    identity: PersonaIdentity,
    memories: list[str],
    current_location: str,
    current_time: datetime,
    context: str,
    interval: list[int],
    consider_identity_persona: bool = True,
):
    lm = model.start_chain(identity.name, "fishing_cognition_act", "choose_act_options")

    with user():
        lm += f"{get_sytem_prompt(identity)}\n"
        lm += location_time_info(current_location, current_time)
        lm += memory_prompt(identity, memories)
        lm += f"\n"
        lm += f"Task: With a fishing range set between {interval[0]}-{interval[-1]}, how many tons of fish would you catch this month? "
        if revenge_jack_flag or revenge_others_flag:  # Assuming `flag` is the condition to determine if the function should be called
            lm += revenge_identity_persona_prompt(identity, revenge_jack_flag, revenge_others_flag)
        lm += reasoning_steps_prompt()
        lm += ' Put the final answer after "Answer:", example Answer: N tons.'

    with assistant():
        lm = model.gen(
            lm,
            "reasoning",
            stop_regex=r"Answer:|So, the answer is:|\*\*Answer\*\*:",
            save_stop_text=True,
        )
        lm = model.find(
            lm,
            regex=r"\d+",
            default_value="0",
            stop_regex=f"tons",
            name="option",
        )
        option = int(lm["option"])
        reasoning = lm["reasoning"]

    model.end_chain(identity.name, lm)
    print('act_prompts/action_choose_amount_to_fish', option)
    return option, lm.html()
