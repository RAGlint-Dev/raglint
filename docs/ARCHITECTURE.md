# RAGLint Architecture

Visual overview of RAGLint's architecture and data flow.

## System Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        A[JSON Data File] --> B[CLI Interface]
        C[Python API] --> B
    end
    
    subgraph "Core Processing"
        B --> D[RAGPipelineAnalyzer]
        D --> E[Config Manager]
        E --> F{Smart Metrics?}
        F -->|Yes| G[LLM Factory]
        F -->|No| H[Basic Metrics Only]
        G --> I{Provider}
        I -->|OpenAI| J[OpenAI_LLM]
        I -->|Ollama| K[OllamaLLM]
        I -->|Mock| L[MockLLM]
    end
    
    subgraph "Metrics Engine"
        H --> M[Chunking Metrics]
        H --> N[Retrieval Metrics]
        J --> O[Semantic Matcher]
        J --> P[Faithfulness Scorer]
        K --> O
        K --> P
        L --> O
        L --> P
    end
    
    subgraph "Output Layer"
        M --> Q[Analysis Results]
        N --> Q
        O --> Q
        P --> Q
        Q --> R[HTML Report Generator]
        Q --> S[JSON Export]
        R --> T[Interactive HTML Report]
    end
    
    style D fill:#4CAF50
    style G fill:#2196F3
    style Q fill:#FF9800
    style R fill:#9C27B0
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Analyzer
    participant LLM
    participant Report
    
    User->>CLI: raglint analyze data.json --smart
    CLI->>Analyzer: Initialize with config
    Analyzer->>LLM: Create provider (OpenAI/Ollama/Mock)
    
    loop For each item in data
        Analyzer->>Analyzer: Calculate basic metrics
        Analyzer->>LLM: Score semantic similarity (async)
        LLM-->>Analyzer: Returns score
        Analyzer->>LLM: Score faithfulness (async)
        LLM-->>Analyzer: Returns score & reasoning
    end
    
    Analyzer-->>CLI: AnalysisResult
    CLI->>Report: Generate HTML
    Report-->>User: raglint_report.html
```

## Component Breakdown

### 1. CLI Layer (`cli.py`)
- **Purpose**: Command-line interface
- **Features**: 
  - Argument parsing (Click)
  - Error handling with exit codes
  - Logging integration
  - Progress display

### 2. Core Analyzer (`core.py`)
- **Purpose**: Orchestrates analysis
- **Features**:
  - Sync & async processing
  - Auto mode detection
  - Progress tracking
  - Results aggregation

### 3. LLM Providers (`llm.py`)
- **Purpose**: Abstract LLM interactions
- **Providers**:
  - `OpenAI_LLM`: Async OpenAI client
  - `OllamaLLM`: Async Ollama client
  - `MockLLM`: Testing without APIs

### 4. Metrics (`metrics/`)

#### Chunking (`chunking.py`)
```python
Input: List[str] # Chunks
Output: Dict[str, float]  # {mean, std, min, max}
```

#### Retrieval (`retrieval.py`)
```python
Input: (retrieved: List[str], ground_truth: List[str])
Output: Dict[str, float]  # {precision, recall, mrr, ndcg}
```

#### Semantic (`semantic.py`)
```python
Input: (texts1: List[str], texts2: List[str])
Output: float  # Similarity score 0-1
```

#### Faithfulness (`faithfulness.py`)
```python
Input: (query: str, contexts: List[str], response: str)
Output: (score: float, reasoning: str)
```

### 5. Reporting (`reporting/`)
- **HTML Generator**: Jinja2 templates
- **Features**:
  - Interactive charts (Chart.js)
  - Responsive design
  - Exportable data

## Async Processing Architecture

```mermaid
graph LR
    subgraph "Synchronous (Old)"
        A1[Item 1] --> B1[LLM Call 1]
        B1 --> C1[Item 2]
        C1 --> D1[LLM Call 2]
        D1 --> E1[...]
    end
    
    subgraph "Asynchronous (New)"
        A2[Item 1] --> B2[LLM Call 1]
        A2[Item 2] --> C2[LLM Call 2]
        A2[Item 3] --> D2[LLM Call 3]
        A2[Item N] --> E2[LLM Call N]
        B2 --> F2[Results]
        C2 --> F2
        D2 --> F2
        E2 --> F2
    end
    
    style B1 fill:#f44336
    style D1 fill:#f44336
    style B2 fill:#4CAF50
    style C2 fill:#4CAF50
    style D2 fill:#4CAF50
    style E2 fill:#4CAF50
```

**Performance**: 2-20x faster with async!

## Configuration Flow

```mermaid
graph TD
    A[raglint.yml] --> B{File Exists?}
    B -->|Yes| C[Load YAML]
    B -->|No| D[Use Defaults]
    C --> E[Config Object]
    D --> E
    F[Environment Variables] --> E
    G[CLI Arguments] --> E
    E --> H[Final Configuration]
    
    style H fill:#4CAF50
```

**Priority**: CLI Args > Env Vars > Config File > Defaults

## Testing Architecture

```mermaid
graph TB
    subgraph "Test Suite"
        A[Integration Tests] --> F[53 Tests Total]
        B[Unit Tests] --> F
        C[Async Tests] --> F
        D[CLI Tests] --> F
        E[Error Tests] --> F
    end
    
    F --> G[pytest]
    G --> H[Coverage: 78%]
    G --> I[All Pass ✅]
    
    style F fill:#2196F3
    style H fill:#4CAF50
    style I fill:#4CAF50
```

## Deployment Pipeline

```mermaid
graph LR
    A[Code Push] --> B{Tests Pass?}
    B -->|No| C[Fail Build]
    B -->|Yes| D[Lint & Type Check]
    D --> E{Tag v*?}
    E -->|No| F[Done]
    E -->|Yes| G[Build Package]
    G --> H[Publish to PyPI]
    
    style C fill:#f44336
    style H fill:#4CAF50
```

## File Structure

```
raglint/
├── cli.py              # CLI entry point
├── core.py             # Main analyzer (async)
├── llm.py              # LLM providers (async)
├── config.py           # Configuration
├── logging.py          # Logging setup
├── metrics/
│   ├── chunking.py     # Chunk analysis
│   ├── retrieval.py    # Retrieval metrics
│   ├── semantic.py     # Semantic matching
│   ├── faithfulness.py # Faithfulness (async)
│   └── relevance.py    # Relevance scoring
└── reporting/
    ├── html_generator.py
    └── templates/
        └── report.html
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **CLI** | Click |
| **Async** | asyncio, aiohttp |
| **LLM** | OpenAI, Ollama |
| **Embeddings** | sentence-transformers |
| **Metrics** | scikit-learn, numpy |
| **Templates** | Jinja2 |
| **Charts** | Chart.js |
| **Testing** | pytest, pytest-asyncio |
| **Linting** | ruff, mypy, black |
| **CI/CD** | GitHub Actions |

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Basic Metrics | O(n) | O(n) |
| Retrieval Metrics | O(n·m) | O(n+m) |
| Semantic (Sync) | O(n) | O(n·d) |
| Faithfulness (Sync) | O(n·L) | O(n) |
| Faithfulness (Async) | O(L) | O(n) |

*where n = items, m = contexts, d = embedding dim, L = LLM latency*

## Security Considerations

- ✅ API keys via environment variables
- ✅ YAML config validation
- ✅ Input sanitization
- ✅ No code execution from untrusted sources
- ✅ Secure HTTP connections (HTTPS)

## Extension Points

### Adding New LLM Providers

```python
class CustomLLM(BaseLLM):
    def generate(self, prompt: str) -> str:
        # Synchronous implementation
        pass
    
    async def agenerate(self, prompt: str) -> str:
        # Async implementation
        pass
```

### Adding New Metrics

```python
def custom_metric(data: List[Dict]) -> float:
    # Your metric logic
    return score
```

Register in `metrics/__init__.py`.

## Future Architecture

Planned improvements:

- 🔄 **Caching Layer**: Redis/SQLite for LLM responses
- 📊 **Metrics Dashboard**: Real-time monitoring
- 🔌 **Plugin System**: Custom metrics & providers
- 📦 **Batch API**: Process multiple files
- 🌐 **Web UI**: Browser-based interface

---

**Last Updated**: 2024-11-21  
**Version**: 0.2.0
