# ISA Codex Agents

## SchemaDiffAgent
- Compares structural differences across GS1 schema versions
- Invoked during cross-phase transitions

## ValidatorAgent
- Applies all rule constraints, schema validations, cardinality checks
- Uses reasoningOutput schema for structured explanations

## FederationAgent
- Aggregates partial verdicts, enforces consensus via LangGraph quorum rules

## VotingAgent
- Applies weighted governance and override logic

## ProfileWeightEngine
- Adjusts stakeholder weights and memory impact on governance decisions
