# GAISA Multi-Agent Consensus Flow Simulation

## Objective
Simulate three autonomous standards agents co-authoring and voting on a proposed update to a shared schema clause.

## Agents
- ISA-GS1
- ISA-UN/CEFACT
- ISA-FDA

## Scenario
Proposal: Harmonize the "ProductIdentifier" field structure to support both GTIN and UDI.

### Step 1: Draft
Each agent submits its own schema suggestion.

### Step 2: Diff Analysis
A `SchemaDiffAnalyzer` compares proposed fields and structures.

### Step 3: Consensus Voting
Agents score each suggestion on:
- Compatibility
- Clarity
- Backward-compatibility

Majority vote determines final schema clause.

### Step 4: Publication
Winning version is committed to GAISA ledger and pushed to all federated nodes.
