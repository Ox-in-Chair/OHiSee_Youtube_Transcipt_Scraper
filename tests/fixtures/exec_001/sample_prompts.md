# Prompt Library - EXEC-001 Samples

## System Prompts

### Prompt: You are a helpful coding assistant

**ID**: `prompt_1`
**Category**: System
**Use Case**: Coding assistant role definition

**Source**: Setup Claude Code Agent (@ 12:34)

#### Template

```
You are a helpful coding assistant. Your task is to help with {task}.
```

#### Variables

- `{task}`: Task - Example: example_task

**Generated**: 2025-10-06T12:00:00

---

## User Prompts

### Prompt: Act as a technical expert

**ID**: `prompt_2`
**Category**: System
**Use Case**: AI assistant role definition

**Source**: Setup Claude Code Agent (@ 12:34)

#### Template

```
Act as a technical expert.
Analyze the {input} and provide {format} output.
```

#### Variables

- `{input}`: Input data or text
  - Type: string
  - Example: example_input
- `{format}`: Output format specification
  - Type: string
  - Example: markdown

**Generated**: 2025-10-06T12:00:00

---

## Few-Shot Prompts

### Prompt: Example 1: Input: code, Output

**ID**: `prompt_3`
**Category**: Few-shot
**Use Case**: Few-shot learning examples

**Source**: Setup Claude Code Agent (@ 12:34)

#### Template

```
Example 1: Input: code, Output: review
     Example 2: Input: docs, Output: summary
```

**Generated**: 2025-10-06T12:00:00

---

## Usage Guide

### How to Use These Prompts

1. **Select appropriate category** for your use case
2. **Fill in variables** with your specific values
3. **Test the prompt** with sample data
4. **Iterate and refine** based on results

### Variable Naming Conventions

- Use `{curly_braces}` for standard variables
- Use descriptive names: `{user_input}` not `{x}`
- Document expected format in variable description

### Example Workflow

```python
# 1. Select prompt template
template = "You are a helpful coding assistant. Your task is to help with {task}."

# 2. Fill variables
filled_prompt = template.replace("{task}", "debugging Python code")

# 3. Use with AI model
response = ai_model.complete(filled_prompt)
```
