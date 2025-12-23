# Strudel Agent - Project Seed

## Original Intent

**Date**: 2025-12-22

## Vision

Create an agent with strong coding abilities in Strudel (live coding music environment) that can:
- Understand musical intent from users
- Translate that intent into working Strudel code
- Maintain a toolset of code snippets for different musical effects
- Combine snippets intelligently to achieve desired musical outcomes

## Development Approach

### Phase 1: Agent Design (Current)
1. **Research First**: Comprehensive study of Strudel documentation
   - Focus on: https://strudel.cc/workshop/first-sounds/
   - Extract cheat sheets, code examples, patterns
   - Build comprehensive vocabulary and syntax understanding
   - Collect datasets of working examples

2. **Agent Blueprint**: Create `agents/StrudelCoder.md`
   - Follow `get_agent_coding_instructions` standard
   - Structure:
     - **Vocabulary**: Musical and Strudel-specific terminology
     - **Coding Instructions**: How to translate musical intent to code
     - **Pattern Library**: Common musical patterns and their implementations
     - **Composition Strategies**: How to combine snippets effectively
   - Focus on comprehensive coding instructions since vanilla LLMs need detailed guidance on turning musical intent into usable, combinable code

### Phase 2: Toolset (Future)
- MCP server implementation
- Snippet storage and retrieval system
- Code combination utilities

## Key Challenge

Vanilla LLMs struggle with:
- Understanding musical intent
- Translating intent to Strudel syntax
- Knowing which code patterns achieve specific effects
- Combining snippets in musically coherent ways

**Solution**: Craft a comprehensive agent system prompt BEFORE building toolset, ensuring the agent has deep Strudel knowledge baked into its instructions.

## Success Criteria

Agent should be able to:
- Understand user requests like "make a drum pattern with a shuffle feel"
- Generate working Strudel code that achieves the desired effect
- Recall and combine relevant snippets from its knowledge base
- Explain what the code does musically
