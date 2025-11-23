---
name: Plugin Submission
about: Submit a custom plugin to RAGlint
title: '[PLUGIN] '
labels: plugin, enhancement
assignees: ''
---

## Plugin Information
**Name**: Your Plugin Name
**Version**: 1.0.0
**Author**: Your Name (@your-github-username)

## Description
What does this plugin do? (2-3 sentences)

## Use Cases
When should users use this plugin?
- Use case 1
- Use case 2

## Metrics Provided
What metrics/scores does this plugin calculate?
- `metric_name`: Description (range: 0.0-1.0)

## Code
Link to your plugin code (can be a GitHub Gist, repo, or paste below):

```python
# Your plugin code here
```

## Tests
Have you included tests for your plugin?
- [ ] Yes, tests included
- [ ] No, but will add before merging

## Documentation
- [ ] Docstrings in code
- [ ] Usage example included
- [ ] README or documentation provided

## Example Usage
```python
from your_plugin import YourPlugin

plugin = YourPlugin()
result = await plugin.calculate_async(
    query="example",
    response="example response",
    contexts=["context"]
)
print(result)
# Expected output: {...}
```

## Dependencies
Does your plugin require additional packages?
- [ ] No additional dependencies
- [ ] Yes: list them below

Required packages:
```
package_name>=version
```

## Checklist
- [ ] Plugin follows the PluginInterface
- [ ] Code is well-documented
- [ ] Tests are included
- [ ] No security vulnerabilities
- [ ] MIT license compatible

## Additional Notes
Any other information about your plugin?
