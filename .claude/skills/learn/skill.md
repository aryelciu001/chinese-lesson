# Learn Scenario Skill

Generate and parse a new Chinese conversation scenario in one step.

## Steps

1. Run the **imagine** skill with the given topic — generates the scenario `.md` in `/scenarios/` and determines the English filename used
2. Run the **parse** skill on that same filename — generates the `.json` in `/scenarios-parsed/` and the audio in `/audio/`

## Rules

- Argument is the topic in any language (e.g. `理发`, `taking a taxi`, `at the pharmacy`)
- Determine the English filename chosen by the imagine step before running parse
- No terminal output — all output goes to files

## Trigger

User invokes `/learn [topic]`
