# Project Healthcheck

## ruff (lint)

```
warning: The top-level linter settings are deprecated in favour of their counterparts in the `lint` section. Please update the following options in `pyproject.toml`:
  - 'ignore' -> 'lint.ignore'
  - 'select' -> 'lint.select'
  - 'isort' -> 'lint.isort'
  - 'per-file-ignores' -> 'lint.per-file-ignores'
F541 [*] f-string without any placeholders
  --> ISA_SuperApp/__init__.py:21:14
   |
19 | __description__ = "ISA SuperApp - Intelligent System Architecture"
20 |
21 | logger.debug(f"ISA SuperApp initialization started")
   |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
22 | logger.debug(f"Current working directory: {os.getcwd()}")
23 | logger.debug(
   |
help: Remove extraneous `f` prefix

PTH109 `os.getcwd()` should be replaced by `Path.cwd()`
  --> ISA_SuperApp/__init__.py:22:44
   |
21 | logger.debug(f"ISA SuperApp initialization started")
22 | logger.debug(f"Current working directory: {os.getcwd()}")
   |                                            ^^^^^^^^^
23 | logger.debug(
24 |     f"Available modules in ISA_SuperApp: {os.listdir(os.path.dirname(__file__))}"
   |
help: Replace with `Path.cwd()`

PTH208 Use `pathlib.Path.iterdir()` instead.
  --> ISA_SuperApp/__init__.py:24:43
   |
22 | logger.debug(f"Current working directory: {os.getcwd()}")
23 | logger.debug(
24 |     f"Available modules in ISA_SuperApp: {os.listdir(os.path.dirname(__file__))}"
   |                                           ^^^^^^^^^^
25 | )
   |

PTH120 `os.path.dirname()` should be replaced by `Path.parent`
  --> ISA_SuperApp/__init__.py:24:54
   |
22 | logger.debug(f"Current working directory: {os.getcwd()}")
23 | logger.debug(
24 |     f"Available modules in ISA_SuperApp: {os.listdir(os.path.dirname(__file__))}"
   |                                                      ^^^^^^^^^^^^^^^
25 | )
   |
help: Replace with `Path(...).parent`

RUF022 `__all__` is not sorted
   --> ISA_SuperApp/__init__.py:92:11
    |
 90 |       raise
 91 |
 92 |   __all__ = [
    |  ___________^
 93 | |     # Core
 94 | |     "ISACore",
 95 | |     "ISAConfig",
 96 | |     "ISALogger",
 97 | |     "ISAMetrics",
 98 | |     "ISAException",
 99 | |     "ISAValidationError",
100 | |     # AI/ML
101 | |     "ISAAgent",
102 | |     "ISAModel",
103 | |     "ISAEmbedding",
104 | |     "ISARetriever",
105 | |     "ISAPipeline",
106 | |     "ISATrainer",
107 | |     # Data
108 | |     "ISADataLoader",
109 | |     "ISADataProcessor",
110 | |     "ISADataValidator",
111 | |     "ISADataTransformer",
112 | |     "ISADataStore",
113 | |     # Utils
114 | |     "ISAUtils",
115 | |     "ISACrypto",
116 | |     "ISANetwork",
117 | |     "ISAFileSystem",
118 | |     "ISATime",
119 | |     # Version
120 | |     "get_version_info",
121 | |     # Package info
122 | |     "__version__",
123 | |     "__author__",
124 | |     "__email__",
125 | |     "__license__",
126 | |     "__description__",
127 | | ]
    | |_^
    |
help: Apply an isort-style sorting to `__all__`

F401 [*] `asyncio` imported but unused
  --> ISA_SuperApp/__main__.py:8:8
   |
 6 | """
 7 |
 8 | import asyncio
   |        ^^^^^^^
 9 | import sys
10 | from pathlib import Path
   |
help: Remove unused import: `asyncio`

F401 [*] `typing.List` imported but unused
  --> ISA_SuperApp/cli.py:14:31
   |
12 | from datetime import datetime
13 | from pathlib import Path
14 | from typing import Any, Dict, List, Optional
   |                               ^^^^
15 |
16 | import click
   |
help: Remove unused import: `typing.List`

F401 [*] `.core.app.ISASuperApp` imported but unused
  --> ISA_SuperApp/cli.py:18:23
   |
16 | import click
17 |
18 | from .core.app import ISASuperApp, create_app
   |                       ^^^^^^^^^^^
19 | from .core.config import create_default_config_file, get_config
20 | from .core.exceptions import ISAError
   |
help: Remove unused import: `.core.app.ISASuperApp`

ARG001 Unused function argument: `reload`
  --> ISA_SuperApp/cli.py:59:73
   |
59 | async def _run_server(config_path: Optional[str], host: str, port: int, reload: bool):
   |                                                                         ^^^^^^
60 |     """Run the server."""
61 |     app = await create_app(config_path)
   |

PTH123 `open()` should be replaced by `Path.open()`
   --> ISA_SuperApp/cli.py:173:18
    |
171 |     elif input_file:
172 |         try:
173 |             with open(input_file, "r") as f:
    |                  ^^^^
174 |                 input_data = json.load(f)
175 |         except Exception as e:
    |

UP015 [*] Unnecessary mode argument
   --> ISA_SuperApp/cli.py:173:35
    |
171 |     elif input_file:
172 |         try:
173 |             with open(input_file, "r") as f:
    |                                   ^^^
174 |                 input_data = json.load(f)
175 |         except Exception as e:
    |
help: Remove mode argument

PTH123 `open()` should be replaced by `Path.open()`
   --> ISA_SuperApp/cli.py:291:14
    |
289 |     # Read file content
290 |     try:
291 |         with open(file_path, "r", encoding="utf-8") as f:
    |              ^^^^
292 |             content = f.read()
293 |     except Exception as e:
    |

UP015 [*] Unnecessary mode argument
   --> ISA_SuperApp/cli.py:291:30
    |
289 |     # Read file content
290 |     try:
291 |         with open(file_path, "r", encoding="utf-8") as f:
    |                              ^^^
292 |             content = f.read()
293 |     except Exception as e:
    |
help: Remove mode argument

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/cli.py:294:9
    |
292 |             content = f.read()
293 |     except Exception as e:
294 |         raise ISAError(f"Failed to read file: {e}")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
295 |
296 |     document = Document(
    |

SIM108 Use ternary operator `files = list(dir_path.rglob(pattern)) if recursive else list(dir_path.glob(pattern))` instead of `if`-`else`-block
   --> ISA_SuperApp/cli.py:432:5
    |
430 |       dir_path = Path(directory)
431 |
432 | /     if recursive:
433 | |         files = list(dir_path.rglob(pattern))
434 | |     else:
435 | |         files = list(dir_path.glob(pattern))
    | |____________________________________________^
436 |
437 |       if not files:
    |
help: Replace `if`-`else`-block with `files = list(dir_path.rglob(pattern)) if recursive else list(dir_path.glob(pattern))`

PTH123 `open()` should be replaced by `Path.open()`
   --> ISA_SuperApp/cli.py:446:18
    |
444 |     for file_path in files:
445 |         try:
446 |             with open(file_path, "r", encoding="utf-8") as f:
    |                  ^^^^
447 |                 content = f.read()
    |

UP015 [*] Unnecessary mode argument
   --> ISA_SuperApp/cli.py:446:34
    |
444 |     for file_path in files:
445 |         try:
446 |             with open(file_path, "r", encoding="utf-8") as f:
    |                                  ^^^
447 |                 content = f.read()
    |
help: Remove mode argument

RUF022 [*] `__all__` is not sorted
  --> ISA_SuperApp/core/__init__.py:14:11
   |
12 |   from .metrics import ISAMetrics
13 |
14 |   __all__ = [
   |  ___________^
15 | |     "ISACore",
16 | |     "ISAConfig",
17 | |     "ISALogger",
18 | |     "ISAMetrics",
19 | |     "ISAException",
20 | |     "ISAValidationError",
21 | | ]
   | |_^
   |
help: Apply an isort-style sorting to `__all__`

F401 [*] `json` imported but unused
  --> ISA_SuperApp/core/agent_system.py:11:8
   |
 9 | import asyncio
10 | import enum
11 | import json
   |        ^^^^
12 | import time
13 | import uuid
   |
help: Remove unused import: `json`

F401 [*] `time` imported but unused
  --> ISA_SuperApp/core/agent_system.py:12:8
   |
10 | import enum
11 | import json
12 | import time
   |        ^^^^
13 | import uuid
14 | from dataclasses import dataclass, field
   |
help: Remove unused import: `time`

F401 [*] `typing.Union` imported but unused
  --> ISA_SuperApp/core/agent_system.py:16:62
   |
14 | from dataclasses import dataclass, field
15 | from datetime import datetime
16 | from typing import Any, Callable, Dict, List, Optional, Set, Union
   |                                                              ^^^^^
17 |
18 | from .embedding import BaseEmbeddingProvider, EmbeddingFactory
   |
help: Remove unused import: `typing.Union`

F401 [*] `.embedding.BaseEmbeddingProvider` imported but unused
  --> ISA_SuperApp/core/agent_system.py:18:24
   |
16 | from typing import Any, Callable, Dict, List, Optional, Set, Union
17 |
18 | from .embedding import BaseEmbeddingProvider, EmbeddingFactory
   |                        ^^^^^^^^^^^^^^^^^^^^^
19 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
20 | from .logger import get_logger
   |
help: Remove unused import

F401 [*] `.embedding.EmbeddingFactory` imported but unused
  --> ISA_SuperApp/core/agent_system.py:18:47
   |
16 | from typing import Any, Callable, Dict, List, Optional, Set, Union
17 |
18 | from .embedding import BaseEmbeddingProvider, EmbeddingFactory
   |                                               ^^^^^^^^^^^^^^^^
19 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
20 | from .logger import get_logger
   |
help: Remove unused import

F401 [*] `.exceptions.ISANotFoundError` imported but unused
  --> ISA_SuperApp/core/agent_system.py:19:48
   |
18 | from .embedding import BaseEmbeddingProvider, EmbeddingFactory
19 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
   |                                                ^^^^^^^^^^^^^^^^
20 | from .logger import get_logger
21 | from .models import (
   |
help: Remove unused import: `.exceptions.ISANotFoundError`

F401 [*] `.models.Agent` imported but unused
  --> ISA_SuperApp/core/agent_system.py:22:5
   |
20 | from .logger import get_logger
21 | from .models import (
22 |     Agent,
   |     ^^^^^
23 |     AgentCapability,
24 |     AgentStatus,
   |
help: Remove unused import

F401 [*] `.models.SearchResult` imported but unused
  --> ISA_SuperApp/core/agent_system.py:28:5
   |
26 |     Message,
27 |     MessageType,
28 |     SearchResult,
   |     ^^^^^^^^^^^^
29 |     Task,
30 |     TaskPriority,
   |
help: Remove unused import

SIM105 Use `contextlib.suppress(asyncio.CancelledError)` instead of `try`-`except`-`pass`
   --> ISA_SuperApp/core/agent_system.py:177:13
    |
175 |           if self._task:
176 |               self._task.cancel()
177 | /             try:
178 | |                 await self._task
179 | |             except asyncio.CancelledError:
180 | |                 pass
    | |____________________^
181 |
182 |           self.logger.info(f"Agent {self.agent_id} stopped")
    |
help: Replace with `contextlib.suppress(asyncio.CancelledError)`

F841 Local variable `completion_message` is assigned to but never used
   --> ISA_SuperApp/core/agent_system.py:287:13
    |
286 |             # Send completion message
287 |             completion_message = Message(
    |             ^^^^^^^^^^^^^^^^^^
288 |                 message_id=str(uuid.uuid4()),
289 |                 sender_id=self.agent_id,
    |
help: Remove assignment to unused variable `completion_message`

F841 Local variable `failure_message` is assigned to but never used
   --> ISA_SuperApp/core/agent_system.py:307:13
    |
306 |             # Send failure message
307 |             failure_message = Message(
    |             ^^^^^^^^^^^^^^^
308 |                 message_id=str(uuid.uuid4()),
309 |                 sender_id=self.agent_id,
    |
help: Remove assignment to unused variable `failure_message`

F841 Local variable `params` is assigned to but never used
   --> ISA_SuperApp/core/agent_system.py:489:9
    |
487 |         """Handle command message."""
488 |         command = content.get("command")
489 |         params = content.get("params", {})
    |         ^^^^^^
490 |
491 |         if command == "status":
    |
help: Remove assignment to unused variable `params`

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/agent_system.py:542:13
    |
540 |         except Exception as e:
541 |             self.logger.error(f"Failed to initialize orchestrator: {e}")
542 |             raise ISAConfigurationError(f"Failed to initialize orchestrator: {e}")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
543 |
544 |     async def close(self) -> None:
    |

SIM105 Use `contextlib.suppress(asyncio.CancelledError)` instead of `try`-`except`-`pass`
   --> ISA_SuperApp/core/agent_system.py:551:13
    |
549 |           if self._monitoring_task:
550 |               self._monitoring_task.cancel()
551 | /             try:
552 | |                 await self._monitoring_task
553 | |             except asyncio.CancelledError:
554 | |                 pass
    | |____________________^
555 |
556 |           # Stop all agents
    |
help: Replace with `contextlib.suppress(asyncio.CancelledError)`

F401 [*] `logging` imported but unused
  --> ISA_SuperApp/core/app.py:9:8
   |
 8 | import asyncio
 9 | import logging
   |        ^^^^^^^
10 | import signal
11 | import sys
   |
help: Remove unused import: `logging`

F401 [*] `pathlib.Path` imported but unused
  --> ISA_SuperApp/core/app.py:12:21
   |
10 | import signal
11 | import sys
12 | from pathlib import Path
   |                     ^^^^
13 | from typing import Any, Dict, List, Optional
   |
help: Remove unused import: `pathlib.Path`

F401 [*] `.exceptions.ISANotFoundError` imported but unused
  --> ISA_SuperApp/core/app.py:18:58
   |
16 | from .api import APIServer
17 | from .config import ConfigManager, ISAConfig, get_config
18 | from .exceptions import ISAConfigurationError, ISAError, ISANotFoundError
   |                                                          ^^^^^^^^^^^^^^^^
19 | from .logger import get_logger, setup_logging
20 | from .models import Document, SearchQuery, Task, TaskStatus
   |
help: Remove unused import: `.exceptions.ISANotFoundError`

F401 [*] `.models.TaskStatus` imported but unused
  --> ISA_SuperApp/core/app.py:20:50
   |
18 | from .exceptions import ISAConfigurationError, ISAError, ISANotFoundError
19 | from .logger import get_logger, setup_logging
20 | from .models import Document, SearchQuery, Task, TaskStatus
   |                                                  ^^^^^^^^^^
21 | from .vector_store import VectorStoreManager
22 | from .workflow import WorkflowEngine
   |
help: Remove unused import: `.models.TaskStatus`

ARG001 Unused function argument: `frame`
  --> ISA_SuperApp/core/app.py:57:36
   |
55 |         """Setup signal handlers for graceful shutdown."""
56 |
57 |         def signal_handler(signum, frame):
   |                                    ^^^^^
58 |             self.logger.info(f"Received signal {signum}, initiating shutdown...")
59 |             asyncio.create_task(self.shutdown())
   |

RUF006 Store a reference to the return value of `asyncio.create_task`
  --> ISA_SuperApp/core/app.py:59:13
   |
57 |         def signal_handler(signum, frame):
58 |             self.logger.info(f"Received signal {signum}, initiating shutdown...")
59 |             asyncio.create_task(self.shutdown())
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
60 |
61 |         signal.signal(signal.SIGINT, signal_handler)
   |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
  --> ISA_SuperApp/core/app.py:91:13
   |
89 |         except Exception as e:
90 |             self.logger.error(f"Failed to initialize ISA SuperApp: {e}")
91 |             raise ISAError(f"Application initialization failed: {e}")
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
92 |
93 |     async def _load_configuration(self) -> None:
   |

F401 [*] `asyncio` imported but unused
  --> ISA_SuperApp/core/base_agent.py:8:8
   |
 6 | """
 7 |
 8 | import asyncio
   |        ^^^^^^^
 9 | import time
10 | import uuid
   |
help: Remove unused import: `asyncio`

F401 [*] `typing.Type` imported but unused
  --> ISA_SuperApp/core/base_agent.py:15:57
   |
13 | from datetime import datetime
14 | from enum import Enum
15 | from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
   |                                                         ^^^^
16 |
17 | from .config import ISAConfig
   |
help: Remove unused import

F401 [*] `typing.Union` imported but unused
  --> ISA_SuperApp/core/base_agent.py:15:72
   |
13 | from datetime import datetime
14 | from enum import Enum
15 | from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
   |                                                                        ^^^^^
16 |
17 | from .config import ISAConfig
   |
help: Remove unused import

F541 [*] f-string without any placeholders
   --> ISA_SuperApp/core/base_agent.py:140:13
    |
139 |         self.logger.info(
140 |             f"Agent initialized",
    |             ^^^^^^^^^^^^^^^^^^^^
141 |             agent_id=self.agent_id,
142 |             name=self.name,
    |
help: Remove extraneous `f` prefix

F401 [*] `logging` imported but unused
  --> ISA_SuperApp/core/config.py:10:8
   |
 8 | import enum
 9 | import json
10 | import logging
   |        ^^^^^^^
11 | import os
12 | from dataclasses import asdict, dataclass, field
   |
help: Remove unused import: `logging`

F401 [*] `typing.Union` imported but unused
  --> ISA_SuperApp/core/config.py:15:62
   |
13 | from datetime import datetime
14 | from pathlib import Path
15 | from typing import Any, Dict, List, Optional, Type, TypeVar, Union
   |                                                              ^^^^^
16 |
17 | import yaml
   |
help: Remove unused import: `typing.Union`

F401 [*] `.exceptions.ISAValidationError` imported but unused
  --> ISA_SuperApp/core/config.py:19:48
   |
17 | import yaml
18 |
19 | from .exceptions import ISAConfigurationError, ISAValidationError
   |                                                ^^^^^^^^^^^^^^^^^^
20 | from .logger import get_logger
   |
help: Remove unused import: `.exceptions.ISAValidationError`

F811 Redefinition of unused `logging` from line 10
   --> ISA_SuperApp/core/config.py:282:5
    |
280 |     workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
281 |     api: APIConfig = field(default_factory=APIConfig)
282 |     logging: LoggingConfig = field(default_factory=LoggingConfig)
    |     ^^^^^^^ `logging` redefined here
283 |     monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
284 |     security: SecurityConfig = field(default_factory=SecurityConfig)
    |
   ::: ISA_SuperApp/core/config.py:10:8
    |
  8 | import enum
  9 | import json
 10 | import logging
    |        ------- previous definition of `logging` here
 11 | import os
 12 | from dataclasses import asdict, dataclass, field
    |
help: Remove definition: `logging`

PTH123 `open()` should be replaced by `Path.open()`
   --> ISA_SuperApp/core/config.py:368:18
    |
366 |                 return
367 |
368 |             with open(path, "r", encoding="utf-8") as f:
    |                  ^^^^
369 |                 if path.suffix.lower() in [".yaml", ".yml"]:
370 |                     data = yaml.safe_load(f)
    |

UP015 [*] Unnecessary mode argument
   --> ISA_SuperApp/core/config.py:368:29
    |
366 |                 return
367 |
368 |             with open(path, "r", encoding="utf-8") as f:
    |                             ^^^
369 |                 if path.suffix.lower() in [".yaml", ".yml"]:
370 |                     data = yaml.safe_load(f)
    |
help: Remove mode argument

SIM118 Use `key in dict` instead of `key in dict.keys()`
   --> ISA_SuperApp/core/config.py:384:17
    |
382 |             # Record metadata
383 |             timestamp = datetime.utcnow()
384 |             for key in self._flatten_dict(data).keys():
    |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
385 |                 self._metadata[key] = ConfigMetadata(
386 |                     source=ConfigSource.FILE,
    |
help: Remove `.keys()`

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/config.py:396:13
    |
394 |           except Exception as e:
395 |               self.logger.error(f"Error loading configuration from file {file_path}: {e}")
396 | /             raise ISAConfigurationError(
397 | |                 f"Failed to load configuration from {file_path}: {e}"
398 | |             )
    | |_____________^
399 |
400 |       def _load_from_environment(self) -> None:
    |

E721 Use `is` and `is not` for type comparisons, or `isinstance()` for isinstance checks
   --> ISA_SuperApp/core/config.py:487:12
    |
485 |     def _convert_value(self, value: str, value_type: Type[T]) -> T:
486 |         """Convert string value to specified type."""
487 |         if value_type == bool:
    |            ^^^^^^^^^^^^^^^^^^
488 |             return value.lower() in ("true", "1", "yes", "on")
489 |         elif value_type == int:
    |

E721 Use `is` and `is not` for type comparisons, or `isinstance()` for isinstance checks
   --> ISA_SuperApp/core/config.py:489:14
    |
487 |         if value_type == bool:
488 |             return value.lower() in ("true", "1", "yes", "on")
489 |         elif value_type == int:
    |              ^^^^^^^^^^^^^^^^^
490 |             return int(value)
491 |         elif value_type == float:
    |

E721 Use `is` and `is not` for type comparisons, or `isinstance()` for isinstance checks
   --> ISA_SuperApp/core/config.py:491:14
    |
489 |         elif value_type == int:
490 |             return int(value)
491 |         elif value_type == float:
    |              ^^^^^^^^^^^^^^^^^^^
492 |             return float(value)
493 |         elif value_type == list:
    |

E721 Use `is` and `is not` for type comparisons, or `isinstance()` for isinstance checks
   --> ISA_SuperApp/core/config.py:493:14
    |
491 |         elif value_type == float:
492 |             return float(value)
493 |         elif value_type == list:
    |              ^^^^^^^^^^^^^^^^^^
494 |             return [item.strip() for item in value.split(",")]
495 |         else:
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/config.py:590:13
    |
588 |         except Exception as e:
589 |             self.logger.error(f"Error setting configuration key {key}: {e}")
590 |             raise ISAConfigurationError(f"Failed to set configuration {key}: {e}")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
591 |
592 |     def get_metadata(self, key: str) -> Optional[ConfigMetadata]:
    |

PTH123 `open()` should be replaced by `Path.open()`
   --> ISA_SuperApp/core/config.py:621:18
    |
619 |             path.parent.mkdir(parents=True, exist_ok=True)
620 |
621 |             with open(path, "w", encoding="utf-8") as f:
    |                  ^^^^
622 |                 if format.lower() == "yaml":
623 |                     yaml.safe_dump(data, f, default_flow_style=False)
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/config.py:633:13
    |
631 |         except Exception as e:
632 |             self.logger.error(f"Error saving configuration to {file_path}: {e}")
633 |             raise ISAConfigurationError(f"Failed to save configuration: {e}")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
634 |
635 |     def reload(self) -> None:
    |

F401 [*] `json` imported but unused
  --> ISA_SuperApp/core/embedding.py:10:8
   |
 8 | import abc
 9 | import asyncio
10 | import json
   |        ^^^^
11 | import time
12 | from dataclasses import dataclass
   |
help: Remove unused import: `json`

F401 [*] `time` imported but unused
  --> ISA_SuperApp/core/embedding.py:11:8
   |
 9 | import asyncio
10 | import json
11 | import time
   |        ^^^^
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Tuple, Type, Union
   |
help: Remove unused import: `time`

F401 [*] `typing.Tuple` imported but unused
  --> ISA_SuperApp/core/embedding.py:13:47
   |
11 | import time
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Tuple, Type, Union
   |                                               ^^^^^
14 |
15 | import numpy as np
   |
help: Remove unused import

F401 [*] `typing.Union` imported but unused
  --> ISA_SuperApp/core/embedding.py:13:60
   |
11 | import time
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Tuple, Type, Union
   |                                                            ^^^^^
14 |
15 | import numpy as np
   |
help: Remove unused import

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/embedding.py:225:13
    |
224 |           except ImportError:
225 | /             raise ISAConfigurationError(
226 | |                 "Sentence Transformers not installed. Install with: pip install sentence-transformers"
227 | |             )
    | |_____________^
228 |           except Exception as e:
229 |               self.logger.error(
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/embedding.py:232:13
    |
230 |                   f"Failed to initialize Sentence Transformers embedding provider: {e}"
231 |               )
232 | /             raise ISAConfigurationError(
233 | |                 f"Failed to initialize Sentence Transformers embedding provider: {e}"
234 | |             )
    | |_____________^
235 |
236 |       async def close(self) -> None:
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/embedding.py:263:13
    |
261 |           except Exception as e:
262 |               self.logger.error(f"Failed to embed text with Sentence Transformers: {e}")
263 | /             raise ISAConfigurationError(
264 | |                 f"Failed to embed text with Sentence Transformers: {e}"
265 | |             )
    | |_____________^
266 |
267 |       async def embed_texts(self, texts: List[str]) -> List[List[float]]:
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/embedding.py:293:13
    |
291 |           except Exception as e:
292 |               self.logger.error(f"Failed to embed texts with Sentence Transformers: {e}")
293 | /             raise ISAConfigurationError(
294 | |                 f"Failed to embed texts with Sentence Transformers: {e}"
295 | |             )
    | |_____________^
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/embedding.py:325:13
    |
324 |           except ImportError:
325 | /             raise ISAConfigurationError(
326 | |                 "OpenAI not installed. Install with: pip install openai"
327 | |             )
    | |_____________^
328 |           except Exception as e:
329 |               self.logger.error(f"Failed to initialize OpenAI embedding provider: {e}")
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/embedding.py:330:13
    |
328 |           except Exception as e:
329 |               self.logger.error(f"Failed to initialize OpenAI embedding provider: {e}")
330 | /             raise ISAConfigurationError(
331 | |                 f"Failed to initialize OpenAI embedding provider: {e}"
332 | |             )
    | |_____________^
333 |
334 |       async def close(self) -> None:
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/embedding.py:366:13
    |
364 |         except Exception as e:
365 |             self.logger.error(f"Failed to embed text with OpenAI: {e}")
366 |             raise ISAConfigurationError(f"Failed to embed text with OpenAI: {e}")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
367 |
368 |     async def embed_texts(self, texts: List[str]) -> List[List[float]]:
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/embedding.py:396:13
    |
394 |         except Exception as e:
395 |             self.logger.error(f"Failed to embed texts with OpenAI: {e}")
396 |             raise ISAConfigurationError(f"Failed to embed texts with OpenAI: {e}")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |

F401 [*] `typing.Union` imported but unused
  --> ISA_SuperApp/core/logger.py:16:41
   |
14 | from logging.handlers import RotatingFileHandler
15 | from pathlib import Path
16 | from typing import Any, Dict, Optional, Union
   |                                         ^^^^^
17 |
18 | from .config import ISAConfig, LogLevel
   |
help: Remove unused import: `typing.Union`

F401 [*] `.exceptions.ISAConfigurationError` imported but unused
  --> ISA_SuperApp/core/logger.py:19:25
   |
18 | from .config import ISAConfig, LogLevel
19 | from .exceptions import ISAConfigurationError
   |                         ^^^^^^^^^^^^^^^^^^^^^
   |
help: Remove unused import: `.exceptions.ISAConfigurationError`

F402 Import `field` from line 9 shadowed by loop variable
   --> ISA_SuperApp/core/models.py:164:13
    |
163 |         # Convert datetime strings
164 |         for field in ["created_at", "updated_at", "processed_at"]:
    |             ^^^^^
165 |             if isinstance(data.get(field), str):
166 |                 data[field] = datetime.fromisoformat(data[field])
    |

F402 Import `field` from line 9 shadowed by loop variable
   --> ISA_SuperApp/core/models.py:276:13
    |
274 |         """Create from dictionary."""
275 |         # Convert datetime
276 |         for field in ["created_at", "updated_at"]:
    |             ^^^^^
277 |             if isinstance(data.get(field), str):
278 |                 data[field] = datetime.fromisoformat(data[field])
    |

F402 Import `field` from line 9 shadowed by loop variable
   --> ISA_SuperApp/core/models.py:416:13
    |
414 |         """Create from dictionary."""
415 |         # Convert datetime
416 |         for field in ["created_at", "started_at", "completed_at"]:
    |             ^^^^^
417 |             if isinstance(data.get(field), str):
418 |                 data[field] = datetime.fromisoformat(data[field])
    |

F402 Import `field` from line 9 shadowed by loop variable
   --> ISA_SuperApp/core/models.py:479:13
    |
477 |         """Create from dictionary."""
478 |         # Convert datetime
479 |         for field in ["created_at", "updated_at", "last_accessed"]:
    |             ^^^^^
480 |             if isinstance(data.get(field), str):
481 |                 data[field] = datetime.fromisoformat(data[field])
    |

F402 Import `field` from line 9 shadowed by loop variable
   --> ISA_SuperApp/core/models.py:546:13
    |
544 |         """Create from dictionary."""
545 |         # Convert datetime
546 |         for field in ["created_at", "updated_at"]:
    |             ^^^^^
547 |             if isinstance(data.get(field), str):
548 |                 data[field] = datetime.fromisoformat(data[field])
    |

F401 [*] `json` imported but unused
  --> ISA_SuperApp/core/retrieval.py:10:8
   |
 8 | import abc
 9 | import asyncio
10 | import json
   |        ^^^^
11 | import time
12 | from dataclasses import dataclass
   |
help: Remove unused import: `json`

F401 [*] `time` imported but unused
  --> ISA_SuperApp/core/retrieval.py:11:8
   |
 9 | import asyncio
10 | import json
11 | import time
   |        ^^^^
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |
help: Remove unused import: `time`

F401 [*] `typing.Set` imported but unused
  --> ISA_SuperApp/core/retrieval.py:13:47
   |
11 | import time
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |                                               ^^^
14 |
15 | import numpy as np
   |
help: Remove unused import

F401 [*] `typing.Tuple` imported but unused
  --> ISA_SuperApp/core/retrieval.py:13:52
   |
11 | import time
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |                                                    ^^^^^
14 |
15 | import numpy as np
   |
help: Remove unused import

F401 [*] `typing.Union` imported but unused
  --> ISA_SuperApp/core/retrieval.py:13:59
   |
11 | import time
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |                                                           ^^^^^
14 |
15 | import numpy as np
   |
help: Remove unused import

F401 [*] `numpy` imported but unused
  --> ISA_SuperApp/core/retrieval.py:15:17
   |
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
14 |
15 | import numpy as np
   |                 ^^
16 |
17 | from .embedding import BaseEmbeddingProvider, EmbeddingFactory
   |
help: Remove unused import: `numpy`

F401 [*] `.exceptions.ISANotFoundError` imported but unused
  --> ISA_SuperApp/core/retrieval.py:18:48
   |
17 | from .embedding import BaseEmbeddingProvider, EmbeddingFactory
18 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
   |                                                ^^^^^^^^^^^^^^^^
19 | from .logger import get_logger
20 | from .models import Document, RetrievalStrategy, SearchResult, Vector
   |
help: Remove unused import: `.exceptions.ISANotFoundError`

F401 [*] `.models.RetrievalStrategy` imported but unused
  --> ISA_SuperApp/core/retrieval.py:20:31
   |
18 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
19 | from .logger import get_logger
20 | from .models import Document, RetrievalStrategy, SearchResult, Vector
   |                               ^^^^^^^^^^^^^^^^^
21 | from .vector_store import BaseVectorStore, VectorStoreConfig, VectorStoreFactory
   |
help: Remove unused import: `.models.RetrievalStrategy`

F841 Local variable `all_vectors` is assigned to but never used
   --> ISA_SuperApp/core/retrieval.py:409:9
    |
408 |         query_words = set(query.lower().split())
409 |         all_vectors = []
    |         ^^^^^^^^^^^
410 |
411 |         # Get all vectors (in a real system, this would be more efficient)
    |
help: Remove assignment to unused variable `all_vectors`

B007 Loop control variable `vector_id` not used within loop body
   --> ISA_SuperApp/core/retrieval.py:480:13
    |
478 |         # Calculate combined scores
479 |         combined_results = []
480 |         for vector_id, scores in result_map.items():
    |             ^^^^^^^^^
481 |             combined_score = (
482 |                 self.config.dense_weight * scores["dense_score"]
    |
help: Rename unused `vector_id` to `_vector_id`

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/retrieval.py:583:13
    |
581 |         except Exception as e:
582 |             self.logger.error(f"Failed to initialize retrieval system: {e}")
583 |             raise ISAConfigurationError(f"Failed to initialize retrieval system: {e}")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
584 |
585 |     async def close(self) -> None:
    |

F401 [*] `json` imported but unused
  --> ISA_SuperApp/core/vector_store.py:10:8
   |
 8 | import abc
 9 | import asyncio
10 | import json
   |        ^^^^
11 | import time
12 | from dataclasses import dataclass
   |
help: Remove unused import: `json`

F401 [*] `time` imported but unused
  --> ISA_SuperApp/core/vector_store.py:11:8
   |
 9 | import asyncio
10 | import json
11 | import time
   |        ^^^^
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |
help: Remove unused import: `time`

F401 [*] `typing.Set` imported but unused
  --> ISA_SuperApp/core/vector_store.py:13:47
   |
11 | import time
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |                                               ^^^
14 |
15 | import numpy as np
   |
help: Remove unused import

F401 [*] `typing.Tuple` imported but unused
  --> ISA_SuperApp/core/vector_store.py:13:52
   |
11 | import time
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |                                                    ^^^^^
14 |
15 | import numpy as np
   |
help: Remove unused import

F401 [*] `typing.Union` imported but unused
  --> ISA_SuperApp/core/vector_store.py:13:59
   |
11 | import time
12 | from dataclasses import dataclass
13 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |                                                           ^^^^^
14 |
15 | import numpy as np
   |
help: Remove unused import

F401 [*] `.exceptions.ISANotFoundError` imported but unused
  --> ISA_SuperApp/core/vector_store.py:17:48
   |
15 | import numpy as np
16 |
17 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
   |                                                ^^^^^^^^^^^^^^^^
18 | from .logger import get_logger
19 | from .models import SearchResult, Vector, VectorStoreProvider
   |
help: Remove unused import: `.exceptions.ISANotFoundError`

F401 [*] `.models.VectorStoreProvider` imported but unused
  --> ISA_SuperApp/core/vector_store.py:19:43
   |
17 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
18 | from .logger import get_logger
19 | from .models import SearchResult, Vector, VectorStoreProvider
   |                                           ^^^^^^^^^^^^^^^^^^^
   |
help: Remove unused import: `.models.VectorStoreProvider`

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/vector_store.py:480:13
    |
479 |           except ImportError:
480 | /             raise ISAConfigurationError(
481 | |                 "ChromaDB not installed. Install with: pip install chromadb"
482 | |             )
    | |_____________^
483 |           except Exception as e:
484 |               self.logger.error(f"Failed to initialize ChromaDB vector store: {e}")
    |

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
   --> ISA_SuperApp/core/vector_store.py:485:13
    |
483 |           except Exception as e:
484 |               self.logger.error(f"Failed to initialize ChromaDB vector store: {e}")
485 | /             raise ISAConfigurationError(
486 | |                 f"Failed to initialize ChromaDB vector store: {e}"
487 | |             )
    | |_____________^
488 |
489 |       async def close(self) -> None:
    |

C416 Unnecessary dict comprehension (rewrite using `dict()`)
   --> ISA_SuperApp/core/vector_store.py:560:30
    |
558 |                     vector=results["embeddings"][0][i],
559 |                     document_id=vector_id,
560 |                     metadata={k: v for k, v in results["metadatas"][0][i].items()},
    |                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
561 |                 )
    |
help: Rewrite using `dict()`

C416 Unnecessary dict comprehension (rewrite using `dict()`)
   --> ISA_SuperApp/core/vector_store.py:607:26
    |
605 |                 vector=result["embeddings"][0],
606 |                 document_id=result["ids"][0],
607 |                 metadata={k: v for k, v in result["metadatas"][0].items()},
    |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
608 |             )
    |
help: Rewrite using `dict()`

F821 Undefined name `Type`
   --> ISA_SuperApp/core/vector_store.py:685:47
    |
683 |     @classmethod
684 |     def register_store(
685 |         cls, provider_name: str, store_class: Type[BaseVectorStore]
    |                                               ^^^^
686 |     ) -> None:
687 |         """
    |

F401 [*] `json` imported but unused
  --> ISA_SuperApp/core/workflow.py:11:8
   |
 9 | import asyncio
10 | import enum
11 | import json
   |        ^^^^
12 | import time
13 | import uuid
   |
help: Remove unused import: `json`

F401 [*] `typing.Callable` imported but unused
  --> ISA_SuperApp/core/workflow.py:16:25
   |
14 | from dataclasses import dataclass, field
15 | from datetime import datetime
16 | from typing import Any, Callable, Dict, List, Optional, Set, Union
   |                         ^^^^^^^^
17 |
18 | from .agent_system import AgentOrchestrator, BaseAgent, ResearchAgent
   |
help: Remove unused import

F401 [*] `typing.Set` imported but unused
  --> ISA_SuperApp/core/workflow.py:16:57
   |
14 | from dataclasses import dataclass, field
15 | from datetime import datetime
16 | from typing import Any, Callable, Dict, List, Optional, Set, Union
   |                                                         ^^^
17 |
18 | from .agent_system import AgentOrchestrator, BaseAgent, ResearchAgent
   |
help: Remove unused import

F401 [*] `typing.Union` imported but unused
  --> ISA_SuperApp/core/workflow.py:16:62
   |
14 | from dataclasses import dataclass, field
15 | from datetime import datetime
16 | from typing import Any, Callable, Dict, List, Optional, Set, Union
   |                                                              ^^^^^
17 |
18 | from .agent_system import AgentOrchestrator, BaseAgent, ResearchAgent
   |
help: Remove unused import

F401 [*] `.agent_system.BaseAgent` imported but unused
  --> ISA_SuperApp/core/workflow.py:18:46
   |
16 | from typing import Any, Callable, Dict, List, Optional, Set, Union
17 |
18 | from .agent_system import AgentOrchestrator, BaseAgent, ResearchAgent
   |                                              ^^^^^^^^^
19 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
20 | from .logger import get_logger
   |
help: Remove unused import

F401 [*] `.agent_system.ResearchAgent` imported but unused
  --> ISA_SuperApp/core/workflow.py:18:57
   |
16 | from typing import Any, Callable, Dict, List, Optional, Set, Union
17 |
18 | from .agent_system import AgentOrchestrator, BaseAgent, ResearchAgent
   |                                                         ^^^^^^^^^^^^^
19 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
20 | from .logger import get_logger
   |
help: Remove unused import

F401 [*] `.exceptions.ISAConfigurationError` imported but unused
  --> ISA_SuperApp/core/workflow.py:19:25
   |
18 | from .agent_system import AgentOrchestrator, BaseAgent, ResearchAgent
19 | from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
   |                         ^^^^^^^^^^^^^^^^^^^^^
20 | from .logger import get_logger
21 | from .models import (
   |
help: Remove unused import: `.exceptions.ISAConfigurationError`

F401 [*] `.models.AgentType` imported but unused
  --> ISA_SuperApp/core/workflow.py:23:5
   |
21 | from .models import (
22 |     AgentCapability,
23 |     AgentType,
   |     ^^^^^^^^^
24 |     Document,
25 |     SearchResult,
   |
help: Remove unused import

F401 [*] `.models.Document` imported but unused
  --> ISA_SuperApp/core/workflow.py:24:5
   |
22 |     AgentCapability,
23 |     AgentType,
24 |     Document,
   |     ^^^^^^^^
25 |     SearchResult,
26 |     Task,
   |
help: Remove unused import

F401 [*] `.models.SearchResult` imported but unused
  --> ISA_SuperApp/core/workflow.py:25:5
   |
23 |     AgentType,
24 |     Document,
25 |     SearchResult,
   |     ^^^^^^^^^^^^
26 |     Task,
27 |     TaskPriority,
   |
help: Remove unused import

F401 [*] `.models.Task` imported but unused
  --> ISA_SuperApp/core/workflow.py:26:5
   |
24 |     Document,
25 |     SearchResult,
26 |     Task,
   |     ^^^^
27 |     TaskPriority,
28 |     TaskStatus,
   |
help: Remove unused import

C401 Unnecessary generator (rewrite as a set comprehension)
   --> ISA_SuperApp/core/workflow.py:341:41
    |
339 |                   # Check capabilities
340 |                   agent_capabilities = set(agent_status["capabilities"])
341 |                   required_capabilities = set(
    |  _________________________________________^
342 | |                     cap.value for cap in step.required_capabilities
343 | |                 )
    | |_________________^
344 |
345 |                   if required_capabilities.issubset(agent_capabilities):
    |
help: Rewrite as a set comprehension

RUF006 Store a reference to the return value of `asyncio.create_task`
   --> ISA_SuperApp/core/workflow.py:626:9
    |
625 |         # Start execution
626 |         asyncio.create_task(self._execute_workflow_async(workflow, execution))
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
627 |
628 |         self.logger.info(f"Workflow {workflow_id} execution {execution_id} started")
    |

SIM110 Use `return all(field in input_data for field in required_fields)` instead of `for` loop
   --> ISA_SuperApp/core/workflow.py:777:9
    |
775 |           # Simple validation - in a real system, use a proper schema validator
776 |           required_fields = schema.get("required", [])
777 | /         for field in required_fields:
778 | |             if field not in input_data:
779 | |                 return False
780 | |         return True
    | |___________________^
    |
help: Replace with `return all(field in input_data for field in required_fields)`

F402 Import `field` from line 14 shadowed by loop variable
   --> ISA_SuperApp/core/workflow.py:777:13
    |
775 |         # Simple validation - in a real system, use a proper schema validator
776 |         required_fields = schema.get("required", [])
777 |         for field in required_fields:
    |             ^^^^^
778 |             if field not in input_data:
779 |                 return False
    |

F401 [*] `typing.Optional` imported but unused
  --> ISA_SuperApp/version.py:9:26
   |
 7 | import logging
 8 | import sys
 9 | from typing import Dict, Optional, Tuple
   |                          ^^^^^^^^
10 |
11 | __all__ = ["get_version_info", "parse_version", "compare_versions"]
   |
help: Remove unused import: `typing.Optional`

RUF022 [*] `__all__` is not sorted
  --> ISA_SuperApp/version.py:11:11
   |
 9 | from typing import Dict, Optional, Tuple
10 |
11 | __all__ = ["get_version_info", "parse_version", "compare_versions"]
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
12 |
13 | # Set up logging
   |
help: Apply an isort-style sorting to `__all__`

ERA001 Found commented-out code
  --> agent/check.py:30:5
   |
28 |     }
29 |
30 |     # Lint (ruff)
   |     ^^^^^^^^^^^^^
31 |     code, _ = run("ruff format --check . && ruff check .")
32 |     result["results"].append({"gate": "ruff", "ok": code == 0})
   |
help: Remove commented-out code

ARG001 Unused function argument: `threshold_loc`
  --> agent/policy.py:24:52
   |
23 | def is_significant(
24 |     changed: list[str], threshold_files: int = 15, threshold_loc: int = 500
   |                                                    ^^^^^^^^^^^^^
25 | ) -> bool:
26 |     # LOC threshold requires CI context; here we use file count only
   |

C416 Unnecessary list comprehension (rewrite using `list()`)
  --> agent/policy.py:34:21
   |
32 |     for job in pol.get("jobs", []):
33 |         cond = job.get("when", {})
34 |         any_globs = [g for g in cond.get("changed_paths_any", [])]
   |                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
35 |         if any_globs:
36 |             if any(
   |
help: Rewrite using `list()`

SIM102 Use a single `if` statement instead of nested `if` statements
  --> agent/policy.py:35:9
   |
33 |           cond = job.get("when", {})
34 |           any_globs = [g for g in cond.get("changed_paths_any", [])]
35 | /         if any_globs:
36 | |             if any(
37 | |                 any(fnmatch.fnmatch(f, g) for g in any_globs) for f in pr.changed_files
38 | |             ):
   | |______________^
39 |                   return job["id"]
40 |           if cond.get("significance") and is_significant(pr.changed_files):
   |
help: Combine `if` statements using `and`

ARG001 Unused function argument: `pr`
  --> agent/policy.py:46:19
   |
45 | def is_waiver_needed(
46 |     step_id: str, pr: PRContext, policy: dict[str, Any] | None = None
   |                   ^^
47 | ) -> bool:
48 |     pol = policy or load_policy()
   |

RUF100 [*] Unused `noqa` directive (non-enabled: `F401`)
 --> dspy_modules/__init__.py:5:63
  |
3 | Delegates to the canonical implementation under `src.dspy.src.dspy_modules`.
4 | """
5 | from src.dspy.src.dspy_modules.modules import ClassifierStub  # noqa: F401
  |                                                               ^^^^^^^^^^^^
  |
help: Remove unused `noqa` directive

UP006 Use `list` instead of `List` for type annotation
 --> infra/rag/ingest/splitter.py:6:50
  |
6 | def split_text(text: str, max_len: int = 100) -> List[str]:
  |                                                  ^^^^
7 |     """Deterministic splitter for RAG stubs.
  |
help: Replace with `list`

RUF100 [*] Unused `noqa` directive (non-enabled: `F401`)
 --> llm_runtime/__init__.py:5:40
  |
3 | Delegates to the canonical implementation under `src.llm.src.llm_runtime`.
4 | """
5 | from src.llm.src.llm_runtime import (  # noqa: F401
  |                                        ^^^^^^^^^^^^
6 |     BedrockAgentsStub,
7 |     LlmRuntime,
  |
help: Remove unused `noqa` directive

UP006 Use `list` instead of `List` for type annotation
  --> orchestrator/__init__.py:16:12
   |
14 | class PlanResult:
15 |     final: str
16 |     steps: List[str]
   |            ^^^^
   |
help: Replace with `list`

RUF100 [*] Unused `noqa` directive (non-enabled: `F401`)
 --> packages/docs_provider/__init__.py:2:76
  |
1 | # Expose common symbols for compatibility
2 | from .base import DocsProvider, DocsSnippet, NullProvider, ProviderResult  # noqa: F401
  |                                                                            ^^^^^^^^^^^^
3 | from .context7 import Context7Provider, get_provider  # noqa: F401
  |
help: Remove unused `noqa` directive

RUF100 [*] Unused `noqa` directive (non-enabled: `F401`)
 --> packages/docs_provider/__init__.py:3:55
  |
1 | # Expose common symbols for compatibility
2 | from .base import DocsProvider, DocsSnippet, NullProvider, ProviderResult  # noqa: F401
3 | from .context7 import Context7Provider, get_provider  # noqa: F401
  |                                                       ^^^^^^^^^^^^
  |
help: Remove unused `noqa` directive

B009 [*] Do not call `getattr` with a constant attribute value. It is not any safer than normal property access.
  --> packages/docs_provider/base.py:9:16
   |
 7 | _impl = import_module("src.docs_provider.src.docs_provider.base")
 8 |
 9 | DocsProvider = getattr(_impl, "DocsProvider")
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
10 | ProviderResult = getattr(_impl, "ProviderResult")
11 | DocsSnippet = getattr(_impl, "DocsSnippet")
   |
help: Replace `getattr` with attribute access

B009 [*] Do not call `getattr` with a constant attribute value. It is not any safer than normal property access.
  --> packages/docs_provider/base.py:10:18
   |
 9 | DocsProvider = getattr(_impl, "DocsProvider")
10 | ProviderResult = getattr(_impl, "ProviderResult")
   |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11 | DocsSnippet = getattr(_impl, "DocsSnippet")
12 | NullProvider = getattr(_impl, "NullProvider")
   |
help: Replace `getattr` with attribute access

B009 [*] Do not call `getattr` with a constant attribute value. It is not any safer than normal property access.
  --> packages/docs_provider/base.py:11:15
   |
 9 | DocsProvider = getattr(_impl, "DocsProvider")
10 | ProviderResult = getattr(_impl, "ProviderResult")
11 | DocsSnippet = getattr(_impl, "DocsSnippet")
   |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
12 | NullProvider = getattr(_impl, "NullProvider")
   |
help: Replace `getattr` with attribute access

B009 [*] Do not call `getattr` with a constant attribute value. It is not any safer than normal property access.
  --> packages/docs_provider/base.py:12:16
   |
10 | ProviderResult = getattr(_impl, "ProviderResult")
11 | DocsSnippet = getattr(_impl, "DocsSnippet")
12 | NullProvider = getattr(_impl, "NullProvider")
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
help: Replace `getattr` with attribute access

B009 [*] Do not call `getattr` with a constant attribute value. It is not any safer than normal property access.
  --> packages/docs_provider/context7.py:9:20
   |
 7 | _impl = import_module("src.docs_provider.src.docs_provider.context7")
 8 |
 9 | Context7Provider = getattr(_impl, "Context7Provider")
   |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
10 | get_provider = getattr(_impl, "get_provider")
   |
help: Replace `getattr` with attribute access

B009 [*] Do not call `getattr` with a constant attribute value. It is not any safer than normal property access.
  --> packages/docs_provider/context7.py:10:16
   |
 9 | Context7Provider = getattr(_impl, "Context7Provider")
10 | get_provider = getattr(_impl, "get_provider")
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
help: Replace `getattr` with attribute access

E402 Module level import not at top of file
  --> run_research_crew.py:10:1
   |
 8 | sys.path.insert(0, str(project_root))
 9 |
10 | from src.agent_core.agents.planner import PlannerAgent
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11 | from src.agent_core.agents.researcher import ResearcherAgent
12 | from src.agent_core.agents.synthesizer import SynthesizerAgent
   |

E402 Module level import not at top of file
  --> run_research_crew.py:11:1
   |
10 | from src.agent_core.agents.planner import PlannerAgent
11 | from src.agent_core.agents.researcher import ResearcherAgent
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
12 | from src.agent_core.agents.synthesizer import SynthesizerAgent
13 | from src.agent_core.memory.rag_store import RAGMemory
   |

E402 Module level import not at top of file
  --> run_research_crew.py:12:1
   |
10 | from src.agent_core.agents.planner import PlannerAgent
11 | from src.agent_core.agents.researcher import ResearcherAgent
12 | from src.agent_core.agents.synthesizer import SynthesizerAgent
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 | from src.agent_core.memory.rag_store import RAGMemory
14 | from src.docs_provider.context7 import get_provider as get_docs_provider
   |

E402 Module level import not at top of file
  --> run_research_crew.py:13:1
   |
11 | from src.agent_core.agents.researcher import ResearcherAgent
12 | from src.agent_core.agents.synthesizer import SynthesizerAgent
13 | from src.agent_core.memory.rag_store import RAGMemory
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
14 | from src.docs_provider.context7 import get_provider as get_docs_provider
15 | from src.orchestrator.research_graph import ResearchGraph
   |

E402 Module level import not at top of file
  --> run_research_crew.py:14:1
   |
12 | from src.agent_core.agents.synthesizer import SynthesizerAgent
13 | from src.agent_core.memory.rag_store import RAGMemory
14 | from src.docs_provider.context7 import get_provider as get_docs_provider
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
15 | from src.orchestrator.research_graph import ResearchGraph
16 | from src.tools.web_research import WebResearchTool
   |

E402 Module level import not at top of file
  --> run_research_crew.py:15:1
   |
13 | from src.agent_core.memory.rag_store import RAGMemory
14 | from src.docs_provider.context7 import get_provider as get_docs_provider
15 | from src.orchestrator.research_graph import ResearchGraph
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
16 | from src.tools.web_research import WebResearchTool
   |

E402 Module level import not at top of file
  --> run_research_crew.py:16:1
   |
14 | from src.docs_provider.context7 import get_provider as get_docs_provider
15 | from src.orchestrator.research_graph import ResearchGraph
16 | from src.tools.web_research import WebResearchTool
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17 |
18 | # Configure logging
   |

PTH123 `open()` should be replaced by `Path.open()`
   --> run_tests.py:142:14
    |
140 |     # Parse coverage report
141 |     try:
142 |         with open("coverage.xml", "r") as f:
    |              ^^^^
143 |             coverage_data = f.read()
    |

UP015 [*] Unnecessary mode argument
   --> run_tests.py:142:35
    |
140 |     # Parse coverage report
141 |     try:
142 |         with open("coverage.xml", "r") as f:
    |                                   ^^^
143 |             coverage_data = f.read()
    |
help: Remove mode argument

RUF005 Consider `[*kws, name.lower()]` instead of concatenation
   --> scripts/audit_agent_loops.py:108:50
    |
106 |         for name, src, kws in COMPONENTS:
107 |             p = ROOT / src
108 |             rule_ids = rules_for_keywords(rules, kws + [name.lower()])
    |                                                  ^^^^^^^^^^^^^^^^^^^^
109 |             w.writerow([name, src, str(p.exists()), ";".join(rule_ids)])
    |
help: Replace with `[*kws, name.lower()]`

invalid-syntax: Cannot use parentheses within a `with` statement on Python 3.8 (syntax was added in Python 3.9)
  --> scripts/audit_best_practice.py:31:10
   |
29 |     out = root / "docs" / "audit" / "standards_alignment.csv"
30 |     out.parent.mkdir(parents=True, exist_ok=True)
31 |     with (
   |          ^
32 |         catalog.open("r", encoding="utf-8") as f_in,
33 |         out.open("w", newline="", encoding="utf-8") as f_out,
   |

SIM110 Use `return any(path.match(g) for g in NORMATIVE_GLOBS)` instead of `for` loop
  --> scripts/audit_completeness.py:27:5
   |
25 |       if any(part in EXCLUDE_DIRS for part in path.parts):
26 |           return False
27 | /     for g in NORMATIVE_GLOBS:
28 | |         if path.match(g):
29 | |             return True
30 | |     return False
   | |________________^
   |
help: Replace with `return any(path.match(g) for g in NORMATIVE_GLOBS)`

invalid-syntax: Cannot use parentheses within a `with` statement on Python 3.8 (syntax was added in Python 3.9)
  --> scripts/audit_rule_normalize.py:65:10
   |
63 |     out_csv.parent.mkdir(parents=True, exist_ok=True)
64 |
65 |     with (
   |          ^
66 |         rules_csv.open("r", encoding="utf-8") as f_in,
67 |         out_csv.open("w", newline="", encoding="utf-8") as f_out,
   |

ERA001 Found commented-out code
  --> scripts/audit_traceability.py:36:5
   |
34 | def find_evidence(rule_text: str, source_file: str) -> tuple[str, Evidence | None]:
35 |     t = rule_text.lower()
36 |     # Lint (ruff)
   |     ^^^^^^^^^^^^^
37 |     if "ruff" in t or ("lint" in t and "ruff" in source_file.lower()):
38 |         for p in search_paths(
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> scripts/audit_traceability.py:44:5
   |
42 |             if ev:
43 |                 return "PASS", ev
44 |     # Typecheck (mypy)
   |     ^^^^^^^^^^^^^^^^^^
45 |     if "mypy" in t or ("typecheck" in t or "typing" in t):
46 |         for p in search_paths(
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> scripts/audit_traceability.py:52:5
   |
50 |             if ev:
51 |                 return "PASS", ev
52 |     # Tests (pytest)
   |     ^^^^^^^^^^^^^^^^
53 |     if "test" in t or "coverage" in t:
54 |         for p in search_paths([".github/workflows/ci.yml", "ISA_SuperApp/tests/**"]):
   |
help: Remove commented-out code

invalid-syntax: Cannot use parentheses within a `with` statement on Python 3.8 (syntax was added in Python 3.9)
   --> scripts/audit_traceability.py:123:10
    |
121 |     out = root / "docs" / "audit" / "traceability_matrix.csv"
122 |     out.parent.mkdir(parents=True, exist_ok=True)
123 |     with (
    |          ^
124 |         catalog.open("r", encoding="utf-8") as f_in,
125 |         out.open("w", newline="", encoding="utf-8") as f_out,
    |

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/audit_with_issue.py:94:18
   |
92 |         scores = {}
93 |         try:
94 |             with open(audit_report) as f:
   |                  ^^^^
95 |                 content = f.read()
   |

UP024 [*] Replace aliased errors with `OSError`
   --> scripts/audit_with_issue.py:127:16
    |
125 |                     scores["gates_advisory"] = int(match.group(3))
126 |
127 |         except (IOError, ValueError) as e:
    |                ^^^^^^^^^^^^^^^^^^^^^
128 |             print(f"⚠️  Error extracting scores: {e}")
129 |             return {"overall": 0.0, "passes": 0, "warns": 0, "fails": 0}
    |
help: Replace with builtin `OSError`

PTH123 `open()` should be replaced by `Path.open()`
   --> scripts/audit_with_issue.py:139:18
    |
138 |         try:
139 |             with open(self.baseline_file) as f:
    |                  ^^^^
140 |                 return json.load(f)
141 |         except (json.JSONDecodeError, ValueError) as e:
    |

PTH123 `open()` should be replaced by `Path.open()`
   --> scripts/audit_with_issue.py:316:18
    |
314 |             }
315 |
316 |             with open(self.baseline_file, "w") as f:
    |                  ^^^^
317 |                 json.dump(baseline_data, f, indent=2)
318 |         else:
    |

RUF034 Useless `if`-`else` condition
  --> scripts/auto_doc_update.py:77:12
   |
75 |             # Don't fail CI for doc update issues; continue best-effort
76 |             continue
77 |     return 0 if changed_any else 0
   |            ^^^^^^^^^^^^^^^^^^^^^^^
   |

UP006 Use `list` instead of `List` for type annotation
  --> scripts/coherence_audit.py:75:34
   |
75 | def parse_py_edges(text: str) -> List[Tuple[str, str]]:
   |                                  ^^^^
76 |     edges = []
77 |     for m in re.finditer(r"^\s*from\s+([\w\.]+)\s+import\s+", text, re.M):
   |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
  --> scripts/coherence_audit.py:75:39
   |
75 | def parse_py_edges(text: str) -> List[Tuple[str, str]]:
   |                                       ^^^^^
76 |     edges = []
77 |     for m in re.finditer(r"^\s*from\s+([\w\.]+)\s+import\s+", text, re.M):
   |
help: Replace with `tuple`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/coherence_audit.py:90:34
   |
90 | def parse_md_edges(text: str) -> List[Tuple[str, str]]:
   |                                  ^^^^
91 |     edges = []
92 |     for m in re.finditer(r"\[[^\]]+\]\(([^\)]+)\)", text):
   |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
  --> scripts/coherence_audit.py:90:39
   |
90 | def parse_md_edges(text: str) -> List[Tuple[str, str]]:
   |                                       ^^^^^
91 |     edges = []
92 |     for m in re.finditer(r"\[[^\]]+\]\(([^\)]+)\)", text):
   |
help: Replace with `tuple`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/coherence_audit.py:97:36
   |
97 | def collect_terms_py(text: str) -> List[str]:
   |                                    ^^^^
98 |     terms = []
99 |     for m in re.finditer(r"\b([A-Z][A-Z0-9_]{2,})\b", text):
   |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> scripts/coherence_audit.py:105:12
    |
104 | def main() -> int:
105 |     nodes: Dict[str, Node] = {}
    |            ^^^^
106 |     edges: List[Edge] = []
107 |     term_freq: Dict[str, int] = defaultdict(int)
    |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/coherence_audit.py:106:12
    |
104 | def main() -> int:
105 |     nodes: Dict[str, Node] = {}
106 |     edges: List[Edge] = []
    |            ^^^^
107 |     term_freq: Dict[str, int] = defaultdict(int)
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> scripts/coherence_audit.py:107:16
    |
105 |     nodes: Dict[str, Node] = {}
106 |     edges: List[Edge] = []
107 |     term_freq: Dict[str, int] = defaultdict(int)
    |                ^^^^
108 |
109 |     files = list(walk_files(ROOT))
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> scripts/coherence_audit.py:163:12
    |
162 |     # Orphans & dead-ends
163 |     indeg: Dict[str, int] = defaultdict(int)
    |            ^^^^
164 |     outdeg: Dict[str, int] = defaultdict(int)
165 |     for e in edges:
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> scripts/coherence_audit.py:164:13
    |
162 |     # Orphans & dead-ends
163 |     indeg: Dict[str, int] = defaultdict(int)
164 |     outdeg: Dict[str, int] = defaultdict(int)
    |             ^^^^
165 |     for e in edges:
166 |         outdeg[e.src] += 1
    |
help: Replace with `dict`

UP028 Replace `yield` over `for` loop with `yield from`
  --> scripts/docs_ref_lint.py:25:5
   |
24 |   def md_files() -> Iterable[Path]:
25 | /     for p in DOCS.rglob("*.md"):
26 | |         yield p
   | |_______________^
   |
help: Replace with `yield from`

UP006 Use `tuple` instead of `Tuple` for type annotation
  --> scripts/docstring_coverage.py:10:37
   |
10 | def count_docstrings(root: Path) -> Tuple[int, int]:
   |                                     ^^^^^
11 |     total = 0
12 |     documented = 0
   |
help: Replace with `tuple`

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/evaluate_research.py:94:10
   |
92 |     output_file = Path(args.output_path)
93 |     output_file.parent.mkdir(parents=True, exist_ok=True)
94 |     with open(output_file, "w") as f:
   |          ^^^^
95 |         json.dump(evaluation_results, f, indent=4)
   |

SIM110 Use `return any(ap.startswith(pref) for pref in EXCLUDE_PATH_PREFIXES)` instead of `for` loop
  --> scripts/index_repo.py:36:5
   |
34 |           return True
35 |       ap = str(path.resolve())
36 | /     for pref in EXCLUDE_PATH_PREFIXES:
37 | |         if ap.startswith(pref):
38 | |             return True
39 | |     return False
   | |________________^
   |
help: Replace with `return any(ap.startswith(pref) for pref in EXCLUDE_PATH_PREFIXES)`

UP006 Use `dict` instead of `Dict` for type annotation
  --> scripts/inspect_vector_store.py:18:31
   |
18 | def _peek(col, n: int = 5) -> Dict[str, Any]:
   |                               ^^^^
19 |     # Try peek (preferred), fall back to get(limit=...)
20 |     try:
   |
help: Replace with `dict`

B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
  --> scripts/inspect_vector_store.py:26:13
   |
24 |             return col.get(limit=n)
25 |         except Exception as e:
26 |             raise RuntimeError(f"Failed to read collection: {e}")
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |

UP006 Use `list` instead of `List` for type annotation
  --> scripts/inspect_vector_store.py:41:20
   |
41 | def _validate(mds: List[Dict[str, Any]]) -> List[str]:
   |                    ^^^^
42 |     problems: List[str] = []
43 |     for i, md in enumerate(mds):
   |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
  --> scripts/inspect_vector_store.py:41:25
   |
41 | def _validate(mds: List[Dict[str, Any]]) -> List[str]:
   |                         ^^^^
42 |     problems: List[str] = []
43 |     for i, md in enumerate(mds):
   |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/inspect_vector_store.py:41:45
   |
41 | def _validate(mds: List[Dict[str, Any]]) -> List[str]:
   |                                             ^^^^
42 |     problems: List[str] = []
43 |     for i, md in enumerate(mds):
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/inspect_vector_store.py:42:15
   |
41 | def _validate(mds: List[Dict[str, Any]]) -> List[str]:
42 |     problems: List[str] = []
   |               ^^^^
43 |     for i, md in enumerate(mds):
44 |         missing = [k for k in REQUIRED if k not in md]
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/inspect_vector_store.py:50:16
   |
50 | def main(argv: List[str] | None = None) -> int:
   |                ^^^^
51 |     p = argparse.ArgumentParser(
52 |         description="Inspect vector store entries and validate schema fields"
   |
help: Replace with `list`

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/pre_commit_audit.py:43:22
   |
41 |         if config_path.exists():
42 |             try:
43 |                 with open(config_path) as f:
   |                      ^^^^
44 |                     config = json.load(f)
45 |                     return float(config.get("threshold", DEFAULT_THRESHOLD))
   |

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/pre_commit_audit.py:77:18
   |
76 |         try:
77 |             with open(audit_report) as f:
   |                  ^^^^
78 |                 content = f.read()
79 |                 # Look for "Overall Rule Confidence: XX.X %"
   |

UP024 [*] Replace aliased errors with `OSError`
  --> scripts/pre_commit_audit.py:85:16
   |
83 |                 if match:
84 |                     return float(match.group(1))
85 |         except (IOError, ValueError):
   |                ^^^^^^^^^^^^^^^^^^^^^
86 |             pass
   |
help: Replace with builtin `OSError`

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/pre_commit_audit.py:97:18
   |
96 |         try:
97 |             with open(audit_report) as f:
   |                  ^^^^
98 |                 content = f.read()
99 |                 # Look for "PASS: X ✅ | WARN: Y ⚠️ | FAIL: Z ❌"
   |

UP024 [*] Replace aliased errors with `OSError`
   --> scripts/pre_commit_audit.py:107:16
    |
105 |                 if match:
106 |                     return int(match.group(1)), int(match.group(2)), int(match.group(3))
107 |         except IOError:
    |                ^^^^^^^
108 |             pass
    |
help: Replace `IOError` with builtin `OSError`

PTH123 `open()` should be replaced by `Path.open()`
   --> scripts/pre_commit_audit.py:120:18
    |
118 |         suggestions = []
119 |         try:
120 |             with open(remediation_plan) as f:
    |                  ^^^^
121 |                 content = f.read()
122 |                 # Extract checklist items
    |

UP024 [*] Replace aliased errors with `OSError`
   --> scripts/pre_commit_audit.py:129:16
    |
127 |                 incomplete = [item for item in items if not item.startswith("[x]")]
128 |                 suggestions.extend(incomplete[:3])  # Top 3 incomplete items
129 |         except IOError:
    |                ^^^^^^^
130 |             pass
    |
help: Replace `IOError` with builtin `OSError`

PTH123 `open()` should be replaced by `Path.open()`
   --> scripts/pre_commit_audit.py:141:18
    |
140 |         try:
141 |             with open(baseline_file) as f:
    |                  ^^^^
142 |                 baseline_data = json.load(f)
143 |                 baseline_score = float(baseline_data.get("coverage_pct", 0))
    |

UP006 Use `dict` instead of `Dict` for type annotation
  --> scripts/refactor_guard.py:51:21
   |
51 | def load_board() -> Dict[str, Any]:
   |                     ^^^^
52 |     if BOARD_FILE.exists():
53 |         return json.loads(BOARD_FILE.read_text(encoding="utf-8"))
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> scripts/refactor_guard.py:70:23
   |
70 | def save_board(board: Dict[str, Any]) -> None:
   |                       ^^^^
71 |     ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
72 |     BOARD_FILE.write_text(json.dumps(board, indent=2), encoding="utf-8")
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> scripts/refactor_guard.py:75:21
   |
75 | def load_flags() -> Dict[str, Any]:
   |                     ^^^^
76 |     if FLAGS_FILE.exists():
77 |         try:
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> scripts/refactor_guard.py:82:11
   |
80 |             pass
81 |     FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
82 |     init: Dict[str, Any] = {"flags": {}}  # name -> {"enabled": bool, "traffic": int}
   |           ^^^^
83 |     FLAGS_FILE.write_text(json.dumps(init, indent=2), encoding="utf-8")
84 |     return init
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> scripts/refactor_guard.py:87:23
   |
87 | def save_flags(flags: Dict[str, Any]) -> None:
   |                       ^^^^
88 |     FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
89 |     FLAGS_FILE.write_text(json.dumps(flags, indent=2), encoding="utf-8")
   |
help: Replace with `dict`

UP045 Use `X | None` for type annotations
  --> scripts/refactor_guard.py:94:10
   |
92 | def run(
93 |     cmd: str,
94 |     cwd: Optional[Path] = None,
   |          ^^^^^^^^^^^^^^
95 |     check: bool = False,
96 |     env: Optional[Dict[str, str]] = None,
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> scripts/refactor_guard.py:96:10
   |
94 |     cwd: Optional[Path] = None,
95 |     check: bool = False,
96 |     env: Optional[Dict[str, str]] = None,
   |          ^^^^^^^^^^^^^^^^^^^^^^^^
97 | ) -> Tuple[int, str]:
98 |     proc = subprocess.Popen(
   |
help: Convert to `X | None`

UP006 Use `dict` instead of `Dict` for type annotation
  --> scripts/refactor_guard.py:96:19
   |
94 |     cwd: Optional[Path] = None,
95 |     check: bool = False,
96 |     env: Optional[Dict[str, str]] = None,
   |                   ^^^^
97 | ) -> Tuple[int, str]:
98 |     proc = subprocess.Popen(
   |
help: Replace with `dict`

UP006 Use `tuple` instead of `Tuple` for type annotation
  --> scripts/refactor_guard.py:97:6
   |
95 |     check: bool = False,
96 |     env: Optional[Dict[str, str]] = None,
97 | ) -> Tuple[int, str]:
   |      ^^^^^
98 |     proc = subprocess.Popen(
99 |         cmd,
   |
help: Replace with `tuple`

ARG001 Unused function argument: `args`
   --> scripts/refactor_guard.py:117:19
    |
117 | def cmd_bootstrap(args: argparse.Namespace) -> None:
    |                   ^^^^
118 |     board = load_board()
119 |     if board.get("initialized"):
    |

UP045 Use `X | None` for type annotations
   --> scripts/refactor_guard.py:132:18
    |
130 | def _pytest_once(
131 |     with_cov: bool = False,
132 |     cov_out_xml: Optional[Path] = None,
    |                  ^^^^^^^^^^^^^^
133 |     paths: Optional[List[str]] = None,
134 | ) -> Tuple[int, str]:
    |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
   --> scripts/refactor_guard.py:133:12
    |
131 |     with_cov: bool = False,
132 |     cov_out_xml: Optional[Path] = None,
133 |     paths: Optional[List[str]] = None,
    |            ^^^^^^^^^^^^^^^^^^^
134 | ) -> Tuple[int, str]:
135 |     paths = paths or ["src"]
    |
help: Convert to `X | None`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:133:21
    |
131 |     with_cov: bool = False,
132 |     cov_out_xml: Optional[Path] = None,
133 |     paths: Optional[List[str]] = None,
    |                     ^^^^
134 | ) -> Tuple[int, str]:
135 |     paths = paths or ["src"]
    |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
   --> scripts/refactor_guard.py:134:6
    |
132 |     cov_out_xml: Optional[Path] = None,
133 |     paths: Optional[List[str]] = None,
134 | ) -> Tuple[int, str]:
    |      ^^^^^
135 |     paths = paths or ["src"]
136 |     base = "python3 -m pytest -q --maxfail=1"
    |
help: Replace with `tuple`

PTH109 `os.getcwd()` should be replaced by `Path.cwd()`
   --> scripts/refactor_guard.py:142:26
    |
140 |     cmd = f"{base} {' '.join(shlex.quote(p) for p in paths)}"
141 |     # Ensure repo root on PYTHONPATH so compat shims under ./packages are visible
142 |     env = {"PYTHONPATH": os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")}
    |                          ^^^^^^^^^
143 |     rc, out = run(cmd, env=env)
144 |     return rc, out
    |
help: Replace with `Path.cwd()`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:147:52
    |
147 | def _parse_pytest_output_for_failures(out: str) -> List[str]:
    |                                                    ^^^^
148 |     # Extract test node IDs that failed from pytest summary lines
149 |     failed: List[str] = []
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:149:13
    |
147 | def _parse_pytest_output_for_failures(out: str) -> List[str]:
148 |     # Extract test node IDs that failed from pytest summary lines
149 |     failed: List[str] = []
    |             ^^^^
150 |     for line in out.splitlines():
151 |         # Example: FAILED src/orchestrator/tests/test_api_server_smoke.py::test_metrics_endpoint - AssertionError
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:158:71
    |
158 | def _collect_coverage_gaps(cov_xml: Path, threshold: float = 80.0) -> List[str]:
    |                                                                       ^^^^
159 |     try:
160 |         import xml.etree.ElementTree as ET
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:164:15
    |
162 |         tree = ET.parse(str(cov_xml))
163 |         root = tree.getroot()
164 |         gaps: List[str] = []
    |               ^^^^
165 |         for cls in root.iterfind(".//class"):
166 |             fname = cls.attrib.get("filename", "")
    |
help: Replace with `list`

ARG001 Unused function argument: `args`
   --> scripts/refactor_guard.py:183:18
    |
183 | def cmd_precheck(args: argparse.Namespace) -> None:
    |                  ^^^^
184 |     board = load_board()
185 |     log("PRE-CHECK: installing deps (best-effort)")
    |

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:192:19
    |
190 |         run("python3 -m pip install -r requirements-dev.txt", check=False)
191 |     log("PRE-CHECK: running test suite 3x (scoped to src/)")
192 |     all_failures: List[List[str]] = []
    |                   ^^^^
193 |     any_red = False
194 |     for i in range(3):
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:192:24
    |
190 |         run("python3 -m pip install -r requirements-dev.txt", check=False)
191 |     log("PRE-CHECK: running test suite 3x (scoped to src/)")
192 |     all_failures: List[List[str]] = []
    |                        ^^^^
193 |     any_red = False
194 |     for i in range(3):
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:206:12
    |
204 |     # Coverage gaps from first run with coverage
205 |     gaps = _collect_coverage_gaps(ARTIFACTS_DIR / "coverage.xml")
206 |     flaky: List[str] = []
    |            ^^^^
207 |     # Detect flakies by presence/absence across runs
208 |     test_set = set([t for runf in all_failures for t in runf])
    |
help: Replace with `list`

C403 Unnecessary list comprehension (rewrite as a set comprehension)
   --> scripts/refactor_guard.py:208:16
    |
206 |     flaky: List[str] = []
207 |     # Detect flakies by presence/absence across runs
208 |     test_set = set([t for runf in all_failures for t in runf])
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
209 |     for t in sorted(test_set):
210 |         appear = sum(1 for runf in all_failures if t in runf)
    |
help: Rewrite as a set comprehension

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:247:26
    |
247 | def _estimate_loc(files: List[str]) -> int:
    |                          ^^^^
248 |     total = 0
249 |     for f in files:
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:259:27
    |
259 | def _list_repo_files() -> List[str]:
    |                           ^^^^
260 |     rc, out = run("rg --files")
261 |     if rc != 0:
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:273:28
    |
273 | def _load_graph_edges() -> List[Tuple[str, str]]:
    |                            ^^^^
274 |     if COHERENCE_GRAPH.exists():
275 |         try:
    |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
   --> scripts/refactor_guard.py:273:33
    |
273 | def _load_graph_edges() -> List[Tuple[str, str]]:
    |                                 ^^^^^
274 |     if COHERENCE_GRAPH.exists():
275 |         try:
    |
help: Replace with `tuple`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:294:45
    |
294 | def _propose_slices(max_slices: int = 5) -> List[Dict[str, Any]]:
    |                                             ^^^^
295 |     files = _list_repo_files()
296 |     edges = _load_graph_edges()
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> scripts/refactor_guard.py:294:50
    |
294 | def _propose_slices(max_slices: int = 5) -> List[Dict[str, Any]]:
    |                                                  ^^^^
295 |     files = _list_repo_files()
296 |     edges = _load_graph_edges()
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> scripts/refactor_guard.py:297:15
    |
295 |     files = _list_repo_files()
296 |     edges = _load_graph_edges()
297 |     incoming: Dict[str, int] = {f: 0 for f in files}
    |               ^^^^
298 |     for _, d in edges:
299 |         if d in incoming:
    |
help: Replace with `dict`

C420 [*] Unnecessary dict comprehension for iterable; use `dict.fromkeys` instead
   --> scripts/refactor_guard.py:297:32
    |
295 |     files = _list_repo_files()
296 |     edges = _load_graph_edges()
297 |     incoming: Dict[str, int] = {f: 0 for f in files}
    |                                ^^^^^^^^^^^^^^^^^^^^^
298 |     for _, d in edges:
299 |         if d in incoming:
    |
help: Replace with `dict.fromkeys(iterable)`)

UP006 Use `dict` instead of `Dict` for type annotation
   --> scripts/refactor_guard.py:302:13
    |
300 |             incoming[d] += 1
301 |     # Pick small clusters by directory with no or few incoming edges
302 |     by_dir: Dict[str, List[str]] = {}
    |             ^^^^
303 |     for f in files:
304 |         d = str(Path(f).parent)
    |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:302:23
    |
300 |             incoming[d] += 1
301 |     # Pick small clusters by directory with no or few incoming edges
302 |     by_dir: Dict[str, List[str]] = {}
    |                       ^^^^
303 |     for f in files:
304 |         d = str(Path(f).parent)
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:306:17
    |
304 |         d = str(Path(f).parent)
305 |         by_dir.setdefault(d, []).append(f)
306 |     candidates: List[Tuple[str, List[str]]] = []
    |                 ^^^^
307 |     for d, fs in by_dir.items():
308 |         if len(fs) <= 10:
    |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
   --> scripts/refactor_guard.py:306:22
    |
304 |         d = str(Path(f).parent)
305 |         by_dir.setdefault(d, []).append(f)
306 |     candidates: List[Tuple[str, List[str]]] = []
    |                      ^^^^^
307 |     for d, fs in by_dir.items():
308 |         if len(fs) <= 10:
    |
help: Replace with `tuple`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:306:33
    |
304 |         d = str(Path(f).parent)
305 |         by_dir.setdefault(d, []).append(f)
306 |     candidates: List[Tuple[str, List[str]]] = []
    |                                 ^^^^
307 |     for d, fs in by_dir.items():
308 |         if len(fs) <= 10:
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:315:13
    |
313 |     # Sort by estimated LOC ascending (smaller first) to keep slices small
314 |     candidates.sort(key=lambda t: _estimate_loc(t[1]))
315 |     slices: List[Dict[str, Any]] = []
    |             ^^^^
316 |     today = time.strftime("%Y%m%d")
317 |     for i, (d, fs) in enumerate(candidates[:max_slices], start=1):
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> scripts/refactor_guard.py:315:18
    |
313 |     # Sort by estimated LOC ascending (smaller first) to keep slices small
314 |     candidates.sort(key=lambda t: _estimate_loc(t[1]))
315 |     slices: List[Dict[str, Any]] = []
    |                  ^^^^
316 |     today = time.strftime("%Y%m%d")
317 |     for i, (d, fs) in enumerate(candidates[:max_slices], start=1):
    |
help: Replace with `dict`

ARG001 Unused function argument: `args`
   --> scripts/refactor_guard.py:341:15
    |
341 | def cmd_slice(args: argparse.Namespace) -> None:
    |               ^^^^
342 |     board = load_board()
343 |     slices = _propose_slices(max_slices=10)
    |

ARG001 Unused function argument: `args`
   --> scripts/refactor_guard.py:385:14
    |
385 | def cmd_next(args: argparse.Namespace) -> None:
    |              ^^^^
386 |     board = load_board()
387 |     if board.get("blocked"):
    |

RUF100 [*] Unused `noqa` directive (non-enabled: `E501`)
   --> scripts/refactor_guard.py:401:8
    |
399 |     todos_sorted = sorted(
400 |         todos, key=lambda sid: board["slices"][sid]["est_loc"]
401 |     )  # noqa: E501
    |        ^^^^^^^^^^^^
402 |     sid = todos_sorted[0]
403 |     s = board["slices"][sid]
    |
help: Remove unused `noqa` directive

ARG001 Unused function argument: `args`
   --> scripts/refactor_guard.py:443:16
    |
443 | def cmd_status(args: argparse.Namespace) -> None:
    |                ^^^^
444 |     board = load_board()
445 |     print(f"BOARD: {board['name']}")
    |

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:462:13
    |
460 |     # Simulate: removing legacy files matching *legacy*.py under slice files' dirs
461 |     dirs = sorted({str(Path(f).parent) for f in s["files"]})
462 |     legacy: List[str] = []
    |             ^^^^
463 |     for d in dirs:
464 |         for p in Path(d).glob("*legacy*.py"):
    |
help: Replace with `list`

ARG001 Unused function argument: `args`
   --> scripts/refactor_guard.py:478:18
    |
478 | def cmd_rollback(args: argparse.Namespace) -> None:
    |                  ^^^^
479 |     flags = load_flags()
480 |     n = 0
    |

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:494:13
    |
492 | def cmd_merge(args: argparse.Namespace) -> None:
493 |     board = load_board()
494 |     merged: List[str] = []
    |             ^^^^
495 |     for sid in args.slices:
496 |         s = board["slices"].get(sid)
    |
help: Replace with `list`

ARG001 Unused function argument: `args`
   --> scripts/refactor_guard.py:519:17
    |
519 | def cmd_archive(args: argparse.Namespace) -> None:
    |                 ^^^^
520 |     board = load_board()
521 |     archive_dir = ARTIFACTS_DIR / "archive"
    |

UP045 Use `X | None` for type annotations
   --> scripts/refactor_guard.py:587:16
    |
587 | def main(argv: Optional[List[str]] = None) -> None:
    |                ^^^^^^^^^^^^^^^^^^^
588 |     argv = argv or sys.argv[1:]
589 |     parser = build_parser()
    |
help: Convert to `X | None`

UP006 Use `list` instead of `List` for type annotation
   --> scripts/refactor_guard.py:587:25
    |
587 | def main(argv: Optional[List[str]] = None) -> None:
    |                         ^^^^
588 |     argv = argv or sys.argv[1:]
589 |     parser = build_parser()
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/connectors/federal_register.py:23:41
   |
23 | def normalize_fr_entries(data: dict) -> List[FRDoc]:
   |                                         ^^^^
24 |     docs: List[FRDoc] = []
25 |     results = data.get("results", [])
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/connectors/federal_register.py:24:11
   |
23 | def normalize_fr_entries(data: dict) -> List[FRDoc]:
24 |     docs: List[FRDoc] = []
   |           ^^^^
25 |     results = data.get("results", [])
26 |     for it in results:
   |
help: Replace with `list`

SIM105 Use `contextlib.suppress(Exception)` instead of `try`-`except`-`pass`
  --> scripts/research/connectors/federal_register.py:34:9
   |
32 |               continue
33 |           # Normalize date
34 | /         try:
35 | |             pub = datetime.fromisoformat(pub).date().isoformat()
36 | |         except Exception:
37 | |             pass
   | |________________^
38 |           docs.append(
39 |               FRDoc(title=title, html_url=url, publication_date=pub, doc_type=doc_type)
   |
help: Replace with `contextlib.suppress(Exception)`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/connectors/federal_register_live.py:21:6
   |
19 | def fetch_fr_docs(
20 |     query: str, limit: int = 5, *, allow_network: bool = False, timeout: int = 20
21 | ) -> List[FRDoc]:
   |      ^^^^
22 |     """Fetch Federal Register documents via API (optional; default OFF).
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/connectors/federal_register_live.py:34:10
   |
32 |     r.raise_for_status()
33 |     data = r.json()
34 |     out: List[FRDoc] = []
   |          ^^^^
35 |     for it in data.get("results", [])[:limit]:
36 |         title = (it.get("title") or "").strip()
   |
help: Replace with `list`

SIM105 Use `contextlib.suppress(Exception)` instead of `try`-`except`-`pass`
  --> scripts/research/connectors/federal_register_live.py:40:9
   |
38 |           pub = it.get("publication_date") or ""
39 |           doc_type = it.get("type") or ""
40 | /         try:
41 | |             pub = datetime.fromisoformat(pub).date().isoformat()
42 | |         except Exception:
43 | |             pass
   | |________________^
44 |           if title:
45 |               out.append(
   |
help: Replace with `contextlib.suppress(Exception)`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/connectors/w3c_tr.py:23:41
   |
23 | def normalize_tr_entries(data: dict) -> List[TRDoc]:
   |                                         ^^^^
24 |     docs: List[TRDoc] = []
25 |     items = data.get("items", [])
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/connectors/w3c_tr.py:24:11
   |
23 | def normalize_tr_entries(data: dict) -> List[TRDoc]:
24 |     docs: List[TRDoc] = []
   |           ^^^^
25 |     items = data.get("items", [])
26 |     for it in items:
   |
help: Replace with `list`

UP045 Use `X | None` for type annotations
  --> scripts/research/fetcher.py:56:12
   |
54 |     timeout: int = 20,
55 |     audit_log: str | Path = "docs/audit/research_audit.jsonl",
56 | ) -> tuple[Optional[bytes], FetchRecord]:
   |            ^^^^^^^^^^^^^^^
57 |     """Fetch url with caching, optional network, and audit logging.
   |
help: Convert to `X | None`

RUF002 Docstring contains ambiguous `‑` (NON-BREAKING HYPHEN). Did you mean `-` (HYPHEN-MINUS)?
 --> scripts/research/index_docs.py:1:77
  |
1 | """Index normalized research docs into the SuperApp retrieval index (offline‑first).
  |                                                                             ^
2 |
3 | This utility is designed to run in PR CI without network access. It can ingest
  |

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/index_docs.py:33:42
   |
33 | def _normalize_tr_entries(data: dict) -> List[Tuple[str, str, dict]]:
   |                                          ^^^^
34 |     """Return docs as (id, text, meta) tuples from W3C TR style JSON."""
35 |     items = data.get("items", [])
   |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
  --> scripts/research/index_docs.py:33:47
   |
33 | def _normalize_tr_entries(data: dict) -> List[Tuple[str, str, dict]]:
   |                                               ^^^^^
34 |     """Return docs as (id, text, meta) tuples from W3C TR style JSON."""
35 |     items = data.get("items", [])
   |
help: Replace with `tuple`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/index_docs.py:36:11
   |
34 |     """Return docs as (id, text, meta) tuples from W3C TR style JSON."""
35 |     items = data.get("items", [])
36 |     docs: List[Tuple[str, str, dict]] = []
   |           ^^^^
37 |     for it in items:
38 |         title = it.get("title", "").strip()
   |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
  --> scripts/research/index_docs.py:36:16
   |
34 |     """Return docs as (id, text, meta) tuples from W3C TR style JSON."""
35 |     items = data.get("items", [])
36 |     docs: List[Tuple[str, str, dict]] = []
   |                ^^^^^
37 |     for it in items:
38 |         title = it.get("title", "").strip()
   |
help: Replace with `tuple`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/index_docs.py:71:42
   |
71 | def _normalize_fr_entries(data: dict) -> List[Tuple[str, str, dict]]:
   |                                          ^^^^
72 |     """Return docs as (id, text, meta) tuples from Federal Register JSON."""
73 |     results = data.get("results", [])
   |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
  --> scripts/research/index_docs.py:71:47
   |
71 | def _normalize_fr_entries(data: dict) -> List[Tuple[str, str, dict]]:
   |                                               ^^^^^
72 |     """Return docs as (id, text, meta) tuples from Federal Register JSON."""
73 |     results = data.get("results", [])
   |
help: Replace with `tuple`

UP006 Use `list` instead of `List` for type annotation
  --> scripts/research/index_docs.py:74:11
   |
72 |     """Return docs as (id, text, meta) tuples from Federal Register JSON."""
73 |     results = data.get("results", [])
74 |     docs: List[Tuple[str, str, dict]] = []
   |           ^^^^
75 |     for it in results:
76 |         title = (it.get("title") or "").strip()
   |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
  --> scripts/research/index_docs.py:74:16
   |
72 |     """Return docs as (id, text, meta) tuples from Federal Register JSON."""
73 |     results = data.get("results", [])
74 |     docs: List[Tuple[str, str, dict]] = []
   |                ^^^^^
75 |     for it in results:
76 |         title = (it.get("title") or "").strip()
   |
help: Replace with `tuple`

PTH103 `os.makedirs()` should be replaced by `Path.mkdir(parents=True)`
  --> scripts/research/run_poc.py:17:5
   |
16 | def ensure_dir(path):
17 |     os.makedirs(path, exist_ok=True)
   |     ^^^^^^^^^^^
   |
help: Replace with `Path(...).mkdir(parents=True)`

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/research/run_poc.py:21:10
   |
20 | def load_yaml(path):
21 |     with open(path, "r") as f:
   |          ^^^^
22 |         return yaml.safe_load(f)
   |

UP015 [*] Unnecessary mode argument
  --> scripts/research/run_poc.py:21:21
   |
20 | def load_yaml(path):
21 |     with open(path, "r") as f:
   |                     ^^^
22 |         return yaml.safe_load(f)
   |
help: Remove mode argument

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/research/run_poc.py:26:10
   |
25 | def write_yaml(path, data):
26 |     with open(path, "w") as f:
   |          ^^^^
27 |         yaml.safe_dump(data, f)
   |

PTH110 `os.path.exists()` should be replaced by `Path.exists()`
  --> scripts/research/run_poc.py:41:12
   |
39 |     run_id = args.run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
40 |
41 |     if not os.path.exists(manifest_path):
   |            ^^^^^^^^^^^^^^
42 |         print(f"Manifest not found: {manifest_path}")
43 |         sys.exit(2)
   |
help: Replace with `Path(...).exists()`

PTH118 `os.path.join()` should be replaced by `Path` with `/` operator
  --> scripts/research/run_poc.py:48:21
   |
47 |     # Prepare artifact paths
48 |     artifacts_raw = os.path.join(out_dir, "raw")
   |                     ^^^^^^^^^^^^
49 |     artifacts_processed = os.path.join(out_dir, "processed")
50 |     ensure_dir(artifacts_raw)
   |

PTH118 `os.path.join()` should be replaced by `Path` with `/` operator
  --> scripts/research/run_poc.py:49:27
   |
47 |     # Prepare artifact paths
48 |     artifacts_raw = os.path.join(out_dir, "raw")
49 |     artifacts_processed = os.path.join(out_dir, "processed")
   |                           ^^^^^^^^^^^^
50 |     ensure_dir(artifacts_raw)
51 |     ensure_dir(artifacts_processed)
   |

PTH120 `os.path.dirname()` should be replaced by `Path.parent`
  --> scripts/research/run_poc.py:54:16
   |
53 |     # Copy the manifest for traceability
54 |     ensure_dir(os.path.dirname(os.path.join(out_dir, "manifest_copy")))
   |                ^^^^^^^^^^^^^^^
55 |     shutil.copyfile(manifest_path, os.path.join(out_dir, "manifest_copy.yaml"))
   |
help: Replace with `Path(...).parent`

PTH118 `os.path.join()` should be replaced by `Path` with `/` operator
  --> scripts/research/run_poc.py:54:32
   |
53 |     # Copy the manifest for traceability
54 |     ensure_dir(os.path.dirname(os.path.join(out_dir, "manifest_copy")))
   |                                ^^^^^^^^^^^^
55 |     shutil.copyfile(manifest_path, os.path.join(out_dir, "manifest_copy.yaml"))
   |

PTH118 `os.path.join()` should be replaced by `Path` with `/` operator
  --> scripts/research/run_poc.py:55:36
   |
53 |     # Copy the manifest for traceability
54 |     ensure_dir(os.path.dirname(os.path.join(out_dir, "manifest_copy")))
55 |     shutil.copyfile(manifest_path, os.path.join(out_dir, "manifest_copy.yaml"))
   |                                    ^^^^^^^^^^^^
56 |
57 |     # Produce a tiny processed artifact as proof-of-run
   |

PTH118 `os.path.join()` should be replaced by `Path` with `/` operator
  --> scripts/research/run_poc.py:66:16
   |
64 |         "notes": "This is a smoke-run placeholder that does not perform real embedding.",
65 |     }
66 |     write_yaml(os.path.join(artifacts_processed, "processed.yaml"), processed)
   |                ^^^^^^^^^^^^
67 |
68 |     # Write experiment metadata to experiments/{run_id}.yaml
   |

PTH118 `os.path.join()` should be replaced by `Path` with `/` operator
  --> scripts/research/run_poc.py:69:23
   |
68 |     # Write experiment metadata to experiments/{run_id}.yaml
69 |     experiments_dir = os.path.join("experiments")
   |                       ^^^^^^^^^^^^
70 |     ensure_dir(experiments_dir)
71 |     exp_meta = {
   |

PTH118 `os.path.join()` should be replaced by `Path` with `/` operator
  --> scripts/research/run_poc.py:78:16
   |
76 |         "status": "success",
77 |     }
78 |     write_yaml(os.path.join(experiments_dir, f"{run_id}.yaml"), exp_meta)
   |                ^^^^^^^^^^^^
79 |
80 |     print(f"Completed micro-POC run {run_id}; artifacts in {out_dir}")
   |

SIM105 Use `contextlib.suppress(Exception)` instead of `try`-`except`-`pass`
  --> scripts/save_baselines.py:30:17
   |
28 |               p = Path(line)
29 |               if p.exists():
30 | /                 try:
31 | |                     total += p.stat().st_size
32 | |                 except Exception:
33 | |                     pass
   | |________________________^
34 |       except Exception:
35 |           pass
   |
help: Replace with `contextlib.suppress(Exception)`

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/significance_trigger.py:76:14
   |
74 |     gh_out = os.environ.get("GITHUB_OUTPUT")
75 |     if gh_out:
76 |         with open(gh_out, "a", encoding="utf-8") as f:
   |              ^^^^
77 |             f.write(f"significant={'true' if significant else 'false'}\n")
78 |             f.write(f"reason={reason}\n")
   |

SIM105 Use `contextlib.suppress(Exception)` instead of `try`-`except`-`pass`
  --> scripts/size_budget.py:19:17
   |
17 |               p = Path(line)
18 |               if p.exists():
19 | /                 try:
20 | |                     total += p.stat().st_size
21 | |                 except Exception:
22 | |                     pass
   | |________________________^
23 |       except Exception:
24 |           pass
   |
help: Replace with `contextlib.suppress(Exception)`

SIM105 Use `contextlib.suppress(Exception)` instead of `try`-`except`-`pass`
  --> scripts/size_budget.py:46:9
   |
44 |       baseline = {"size": 0, "files": 0}
45 |       if BASELINE.exists():
46 | /         try:
47 | |             baseline = json.loads(BASELINE.read_text())
48 | |         except Exception:
49 | |             pass
   | |________________^
50 |       size_delta = size - baseline.get("size", 0)
51 |       files_delta = files - baseline.get("files", 0)
   |
help: Replace with `contextlib.suppress(Exception)`

F401 [*] `pathlib.Path` imported but unused
 --> scripts/tests/test_ingest_text.py:6:21
  |
4 | import sys
5 | from importlib import import_module
6 | from pathlib import Path
  |                     ^^^^
  |
help: Remove unused import: `pathlib.Path`

PTH123 `open()` should be replaced by `Path.open()`
  --> scripts/validate_audit_mechanisms.py:54:18
   |
52 |             import yaml
53 |
54 |             with open(self.github_action_file) as f:
   |                  ^^^^
55 |                 yaml.safe_load(f)
56 |             self.results.append(("GitHub Action YAML", True, "Valid YAML syntax"))
   |

PTH123 `open()` should be replaced by `Path.open()`
   --> scripts/validate_audit_mechanisms.py:101:18
    |
 99 |             import yaml
100 |
101 |             with open(self.pre_commit_config) as f:
    |                  ^^^^
102 |                 config = yaml.safe_load(f)
103 |             self.results.append(("Pre-commit YAML", True, "Valid YAML syntax"))
    |

PTH123 `open()` should be replaced by `Path.open()`
   --> scripts/validate_audit_mechanisms.py:139:18
    |
138 |         try:
139 |             with open(self.audit_threshold_config) as f:
    |                  ^^^^
140 |                 config_data = json.load(f)
141 |                 threshold = float(config_data.get("threshold", 0))
    |

PTH123 `open()` should be replaced by `Path.open()`
   --> scripts/validate_audit_mechanisms.py:270:18
    |
268 |         # Test audit threshold config
269 |         try:
270 |             with open(self.audit_threshold_config) as f:
    |                  ^^^^
271 |                 config = json.load(f)
272 |                 if config.get("threshold") != 70.0:
    |

PTH123 `open()` should be replaced by `Path.open()`
  --> setup.py:22:10
   |
20 | requirements_path = this_directory / "requirements.txt"
21 | if requirements_path.exists():
22 |     with open(requirements_path, "r", encoding="utf-8") as f:
   |          ^^^^
23 |         requirements = [
24 |             line.strip() for line in f if line.strip() and not line.startswith("#")
   |

UP015 [*] Unnecessary mode argument
  --> setup.py:22:34
   |
20 | requirements_path = this_directory / "requirements.txt"
21 | if requirements_path.exists():
22 |     with open(requirements_path, "r", encoding="utf-8") as f:
   |                                  ^^^
23 |         requirements = [
24 |             line.strip() for line in f if line.strip() and not line.startswith("#")
   |
help: Remove mode argument

RUF022 [*] `__all__` is not sorted
  --> src/agent_core/agent_core/__init__.py:11:11
   |
 9 |   from .verifier import Verifier
10 |
11 |   __all__ = [
   |  ___________^
12 | |     "Planner",
13 | |     "Builder",
14 | |     "Verifier",
15 | |     "Critic",
16 | |     "RewardAggregator",
17 | |     "TraceLogger",
18 | |     "Policy",
19 | | ]
   | |_^
   |
help: Apply an isort-style sorting to `__all__`

C414 Unnecessary `list()` call within `sorted()`
  --> src/agent_core/agents/synthesizer.py:50:23
   |
49 |         report += "\n## Sources Consulted\n\n"
50 |         for source in sorted(list(seen_sources)):
   |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^
51 |             report += f"- {source}\n"
   |
help: Remove the inner `list()` call

TC003 Move standard library import `pathlib.Path` into a type-checking block
 --> src/agent_core/tests/test_rag_memory_schema.py:3:21
  |
1 | from __future__ import annotations
2 |
3 | from pathlib import Path
  |                     ^^^^
4 |
5 | from src.agent_core.memory.rag_store import RAGMemory
  |
help: Move into type-checking block

UP045 Use `X | None` for type annotations
  --> src/docs_provider/base.py:20:18
   |
18 |         source: str
19 |         content: str
20 |         version: Optional[str] = None
   |                  ^^^^^^^^^^^^^
21 |         url: Optional[str] = None
22 |         license: Optional[str] = None
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/base.py:21:14
   |
19 |         content: str
20 |         version: Optional[str] = None
21 |         url: Optional[str] = None
   |              ^^^^^^^^^^^^^
22 |         license: Optional[str] = None
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/base.py:22:18
   |
20 |         version: Optional[str] = None
21 |         url: Optional[str] = None
22 |         license: Optional[str] = None
   |                  ^^^^^^^^^^^^^
23 |
24 |     @dataclass(frozen=True)
   |
help: Convert to `X | None`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/base.py:26:19
   |
24 |     @dataclass(frozen=True)
25 |     class ProviderResult:  # type: ignore[no-redef]
26 |         snippets: List[DocsSnippet]
   |                   ^^^^
27 |
28 |     class DocsProvider(Protocol):  # type: ignore[no-redef]
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/base.py:33:19
   |
31 |             query: str,
32 |             *,
33 |             libs: List[str],
   |                   ^^^^
34 |             version: Optional[str] = None,
35 |             limit: int = 5,
   |
help: Replace with `list`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/base.py:34:22
   |
32 |             *,
33 |             libs: List[str],
34 |             version: Optional[str] = None,
   |                      ^^^^^^^^^^^^^
35 |             limit: int = 5,
36 |             section_hints: Optional[List[str]] = None,
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/base.py:36:28
   |
34 |             version: Optional[str] = None,
35 |             limit: int = 5,
36 |             section_hints: Optional[List[str]] = None,
   |                            ^^^^^^^^^^^^^^^^^^^
37 |         ) -> ProviderResult:
38 |             ...
   |
help: Convert to `X | None`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/base.py:36:37
   |
34 |             version: Optional[str] = None,
35 |             limit: int = 5,
36 |             section_hints: Optional[List[str]] = None,
   |                                     ^^^^
37 |         ) -> ProviderResult:
38 |             ...
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/base.py:45:19
   |
43 |             query: str,
44 |             *,
45 |             libs: List[str],
   |                   ^^^^
46 |             version: Optional[str] = None,
47 |             limit: int = 5,
   |
help: Replace with `list`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/base.py:46:22
   |
44 |             *,
45 |             libs: List[str],
46 |             version: Optional[str] = None,
   |                      ^^^^^^^^^^^^^
47 |             limit: int = 5,
48 |             section_hints: Optional[List[str]] = None,
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/base.py:48:28
   |
46 |             version: Optional[str] = None,
47 |             limit: int = 5,
48 |             section_hints: Optional[List[str]] = None,
   |                            ^^^^^^^^^^^^^^^^^^^
49 |         ) -> ProviderResult:
50 |             return ProviderResult(snippets=[])
   |
help: Convert to `X | None`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/base.py:48:37
   |
46 |             version: Optional[str] = None,
47 |             limit: int = 5,
48 |             section_hints: Optional[List[str]] = None,
   |                                     ^^^^
49 |         ) -> ProviderResult:
50 |             return ProviderResult(snippets=[])
   |
help: Replace with `list`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/src/docs_provider/base.py:13:14
   |
11 |     source: str
12 |     content: str
13 |     version: Optional[str] = None
   |              ^^^^^^^^^^^^^
14 |     url: Optional[str] = None
15 |     license: Optional[str] = None
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/src/docs_provider/base.py:14:10
   |
12 |     content: str
13 |     version: Optional[str] = None
14 |     url: Optional[str] = None
   |          ^^^^^^^^^^^^^
15 |     license: Optional[str] = None
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/src/docs_provider/base.py:15:14
   |
13 |     version: Optional[str] = None
14 |     url: Optional[str] = None
15 |     license: Optional[str] = None
   |              ^^^^^^^^^^^^^
   |
help: Convert to `X | None`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/src/docs_provider/base.py:22:15
   |
20 |     """The result returned by a documentation provider."""
21 |
22 |     snippets: List[DocsSnippet]
   |               ^^^^
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/src/docs_provider/base.py:32:15
   |
30 |         query: str,
31 |         *,
32 |         libs: List[str],
   |               ^^^^
33 |         version: Optional[str] = None,
34 |         limit: int = 5,
   |
help: Replace with `list`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/src/docs_provider/base.py:33:18
   |
31 |         *,
32 |         libs: List[str],
33 |         version: Optional[str] = None,
   |                  ^^^^^^^^^^^^^
34 |         limit: int = 5,
35 |         section_hints: Optional[List[str]] = None,
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/src/docs_provider/base.py:35:24
   |
33 |         version: Optional[str] = None,
34 |         limit: int = 5,
35 |         section_hints: Optional[List[str]] = None,
   |                        ^^^^^^^^^^^^^^^^^^^
36 |     ) -> ProviderResult:
37 |         """Fetches documentation for a given query."""
   |
help: Convert to `X | None`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/src/docs_provider/base.py:35:33
   |
33 |         version: Optional[str] = None,
34 |         limit: int = 5,
35 |         section_hints: Optional[List[str]] = None,
   |                                 ^^^^
36 |     ) -> ProviderResult:
37 |         """Fetches documentation for a given query."""
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/src/docs_provider/base.py:48:15
   |
46 |         query: str,
47 |         *,
48 |         libs: List[str],
   |               ^^^^
49 |         version: Optional[str] = None,
50 |         limit: int = 5,
   |
help: Replace with `list`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/src/docs_provider/base.py:49:18
   |
47 |         *,
48 |         libs: List[str],
49 |         version: Optional[str] = None,
   |                  ^^^^^^^^^^^^^
50 |         limit: int = 5,
51 |         section_hints: Optional[List[str]] = None,
   |
help: Convert to `X | None`

UP045 Use `X | None` for type annotations
  --> src/docs_provider/src/docs_provider/base.py:51:24
   |
49 |         version: Optional[str] = None,
50 |         limit: int = 5,
51 |         section_hints: Optional[List[str]] = None,
   |                        ^^^^^^^^^^^^^^^^^^^
52 |     ) -> ProviderResult:
53 |         return ProviderResult(snippets=[])
   |
help: Convert to `X | None`

UP006 Use `list` instead of `List` for type annotation
  --> src/docs_provider/src/docs_provider/base.py:51:33
   |
49 |         version: Optional[str] = None,
50 |         limit: int = 5,
51 |         section_hints: Optional[List[str]] = None,
   |                                 ^^^^
52 |     ) -> ProviderResult:
53 |         return ProviderResult(snippets=[])
   |
help: Replace with `list`

UP024 [*] Replace aliased errors with `OSError`
  --> src/docs_provider/src/docs_provider/cache.py:39:16
   |
38 |             return data.get("payload")
39 |         except (IOError, json.JSONDecodeError):
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
40 |             return None
   |
help: Replace with builtin `OSError`

UP024 [*] Replace aliased errors with `OSError`
  --> src/docs_provider/src/docs_provider/cache.py:50:16
   |
48 |             with path.open("w", encoding="utf-8") as f:
49 |                 json.dump(data, f)
50 |         except IOError:
   |                ^^^^^^^
51 |             pass  # Fail silently if cache write fails
   |
help: Replace `IOError` with builtin `OSError`

RUF100 [*] Unused `noqa` directive (non-enabled: `F401`)
 --> src/dspy/src/dspy_modules/__init__.py:1:38
  |
1 | from .modules import ClassifierStub  # noqa: F401
  |                                      ^^^^^^^^^^^^
  |
help: Remove unused `noqa` directive

UP006 Use `dict` instead of `Dict` for type annotation
  --> src/feature_flags.py:10:16
   |
10 | def _load() -> Dict[str, Any]:
   |                ^^^^
11 |     if not FLAGS_FILE.exists():
12 |         FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> src/feature_flags.py:20:17
   |
20 | def _save(data: Dict[str, Any]) -> None:
   |                 ^^^^
21 |     FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
22 |     FLAGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
   |
help: Replace with `dict`

RUF100 [*] Unused `noqa` directive (non-enabled: `F401`)
 --> src/llm/src/llm_runtime/__init__.py:1:74
  |
1 | from .runtime import BedrockAgentsStub, LlmRuntime, OpenAIResponsesStub  # noqa: F401
  |                                                                          ^^^^^^^^^^^^
  |
help: Remove unused `noqa` directive

UP006 Use `list` instead of `List` for type annotation
 --> src/llm/src/llm_runtime/runtime.py:7:30
  |
6 | class OpenAIResponsesStub:
7 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
  |                              ^^^^
8 |         return {
9 |             "model": model,
  |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
 --> src/llm/src/llm_runtime/runtime.py:7:35
  |
6 | class OpenAIResponsesStub:
7 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
  |                                   ^^^^
8 |         return {
9 |             "model": model,
  |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
 --> src/llm/src/llm_runtime/runtime.py:7:73
  |
6 | class OpenAIResponsesStub:
7 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
  |                                                                         ^^^^
8 |         return {
9 |             "model": model,
  |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
  --> src/llm/src/llm_runtime/runtime.py:22:30
   |
21 | class BedrockAgentsStub:
22 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
   |                              ^^^^
23 |         return {
24 |             "model": model,
   |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
  --> src/llm/src/llm_runtime/runtime.py:22:35
   |
21 | class BedrockAgentsStub:
22 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
   |                                   ^^^^
23 |         return {
24 |             "model": model,
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> src/llm/src/llm_runtime/runtime.py:22:73
   |
21 | class BedrockAgentsStub:
22 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
   |                                                                         ^^^^
23 |         return {
24 |             "model": model,
   |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
  --> src/llm/src/llm_runtime/runtime.py:42:30
   |
40 |         self._bedrock = BedrockAgentsStub()
41 |
42 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
   |                              ^^^^
43 |         if self.backend == "bedrock":
44 |             return self._bedrock.chat(messages, model, **kw)
   |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
  --> src/llm/src/llm_runtime/runtime.py:42:35
   |
40 |         self._bedrock = BedrockAgentsStub()
41 |
42 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
   |                                   ^^^^
43 |         if self.backend == "bedrock":
44 |             return self._bedrock.chat(messages, model, **kw)
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> src/llm/src/llm_runtime/runtime.py:42:73
   |
40 |         self._bedrock = BedrockAgentsStub()
41 |
42 |     def chat(self, messages: List[Dict[str, str]], model: str, **kw) -> Dict[str, Any]:
   |                                                                         ^^^^
43 |         if self.backend == "bedrock":
44 |             return self._bedrock.chat(messages, model, **kw)
   |
help: Replace with `dict`

RUF100 [*] Unused `noqa` directive (non-enabled: `F401`)
 --> src/orchestrator/src/orchestrator/__init__.py:1:57
  |
1 | from .graph import OrchestratorResult, PlanToolReflect  # noqa: F401
  |                                                         ^^^^^^^^^^^^
2 | from .langgraph_graph import GraphRunner  # noqa: F401
  |
help: Remove unused `noqa` directive

RUF100 [*] Unused `noqa` directive (non-enabled: `F401`)
 --> src/orchestrator/src/orchestrator/__init__.py:2:43
  |
1 | from .graph import OrchestratorResult, PlanToolReflect  # noqa: F401
2 | from .langgraph_graph import GraphRunner  # noqa: F401
  |                                           ^^^^^^^^^^^^
  |
help: Remove unused `noqa` directive

UP006 Use `list` instead of `List` for type annotation
  --> src/orchestrator/src/orchestrator/graph.py:9:12
   |
 7 | @dataclass
 8 | class OrchestratorResult:
 9 |     steps: List[str]
   |            ^^^^
10 |     final: str
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
  --> src/orchestrator/src/orchestrator/langgraph_graph.py:19:12
   |
17 | @dataclass
18 | class LGState:
19 |     steps: List[str]
   |            ^^^^
20 |     goal: str
21 |     final: Optional[str] = None
   |
help: Replace with `list`

UP045 Use `X | None` for type annotations
  --> src/orchestrator/src/orchestrator/langgraph_graph.py:21:12
   |
19 |     steps: List[str]
20 |     goal: str
21 |     final: Optional[str] = None
   |            ^^^^^^^^^^^^^
   |
help: Convert to `X | None`

PTH123 `open()` should be replaced by `Path.open()`
  --> src/tools/web_research.py:48:18
   |
46 |         if cache_path.exists():
47 |             logging.info(f"Cache hit for search query: {query}")
48 |             with open(cache_path, "r") as f:
   |                  ^^^^
49 |                 return json.load(f)
   |

UP015 [*] Unnecessary mode argument
  --> src/tools/web_research.py:48:35
   |
46 |         if cache_path.exists():
47 |             logging.info(f"Cache hit for search query: {query}")
48 |             with open(cache_path, "r") as f:
   |                                   ^^^
49 |                 return json.load(f)
   |
help: Remove mode argument

PTH123 `open()` should be replaced by `Path.open()`
  --> src/tools/web_research.py:56:18
   |
54 |                 results = list(ddgs.text(query, max_results=max_results))
55 |
56 |             with open(cache_path, "w") as f:
   |                  ^^^^
57 |                 json.dump(results, f)
   |

PTH123 `open()` should be replaced by `Path.open()`
  --> src/tools/web_research.py:79:18
   |
77 |         if cache_path.exists():
78 |             logging.info(f"Cache hit for URL: {url}")
79 |             with open(cache_path, "r") as f:
   |                  ^^^^
80 |                 return f.read()
   |

UP015 [*] Unnecessary mode argument
  --> src/tools/web_research.py:79:35
   |
77 |         if cache_path.exists():
78 |             logging.info(f"Cache hit for URL: {url}")
79 |             with open(cache_path, "r") as f:
   |                                   ^^^
80 |                 return f.read()
   |
help: Remove mode argument

PTH123 `open()` should be replaced by `Path.open()`
  --> src/tools/web_research.py:98:18
   |
96 |             clean_text = "\n".join(chunk for chunk in chunks if chunk)
97 |
98 |             with open(cache_path, "w") as f:
   |                  ^^^^
99 |                 f.write(clean_text)
   |

F401 [*] `json` imported but unused
  --> tests/conftest.py:10:8
   |
 9 | import asyncio
10 | import json
   |        ^^^^
11 | import logging
12 | import os
   |
help: Remove unused import: `json`

F401 [*] `os` imported but unused
  --> tests/conftest.py:12:8
   |
10 | import json
11 | import logging
12 | import os
   |        ^^
13 | import tempfile
14 | from pathlib import Path
   |
help: Remove unused import: `os`

F401 [*] `typing.Optional` imported but unused
  --> tests/conftest.py:15:64
   |
13 | import tempfile
14 | from pathlib import Path
15 | from typing import Any, AsyncGenerator, Dict, Generator, List, Optional
   |                                                                ^^^^^^^^
16 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import: `typing.Optional`

F401 [*] `unittest.mock.AsyncMock` imported but unused
  --> tests/conftest.py:16:27
   |
14 | from pathlib import Path
15 | from typing import Any, AsyncGenerator, Dict, Generator, List, Optional
16 | from unittest.mock import AsyncMock, MagicMock, patch
   |                           ^^^^^^^^^
17 |
18 | import pytest
   |
help: Remove unused import

F401 [*] `unittest.mock.patch` imported but unused
  --> tests/conftest.py:16:49
   |
14 | from pathlib import Path
15 | from typing import Any, AsyncGenerator, Dict, Generator, List, Optional
16 | from unittest.mock import AsyncMock, MagicMock, patch
   |                                                 ^^^^^
17 |
18 | import pytest
   |
help: Remove unused import

F401 [*] `pytest_asyncio` imported but unused
  --> tests/conftest.py:19:8
   |
18 | import pytest
19 | import pytest_asyncio
   |        ^^^^^^^^^^^^^^
20 | from _pytest.config import Config
21 | from _pytest.monkeypatch import MonkeyPatch
   |
help: Remove unused import: `pytest_asyncio`

F401 [*] `sqlalchemy.create_engine` imported but unused
   --> tests/conftest.py:157:28
    |
155 |     # This would typically set up a test database
156 |     # For now, we'll use an in-memory SQLite database
157 |     from sqlalchemy import create_engine
    |                            ^^^^^^^^^^^^^
158 |     from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
159 |     from sqlalchemy.orm import sessionmaker
    |
help: Remove unused import: `sqlalchemy.create_engine`

F841 Local variable `conn` is assigned to but never used
   --> tests/conftest.py:165:34
    |
164 |     # Create tables
165 |     async with engine.begin() as conn:
    |                                  ^^^^
166 |         # Import and create your models here
167 |         # await conn.run_sync(Base.metadata.create_all)
    |
help: Remove assignment to unused variable `conn`

ERA001 Found commented-out code
   --> tests/conftest.py:167:9
    |
165 |     async with engine.begin() as conn:
166 |         # Import and create your models here
167 |         # await conn.run_sync(Base.metadata.create_all)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
168 |         pass
    |
help: Remove commented-out code

F401 [*] `fastapi.testclient.TestClient` imported but unused
   --> tests/conftest.py:191:36
    |
189 | async def test_client() -> AsyncGenerator[Any, None]:
190 |     """Provide a test client for the FastAPI application."""
191 |     from fastapi.testclient import TestClient
    |                                    ^^^^^^^^^^
192 |
193 |     # Import your FastAPI app here
    |
help: Remove unused import: `fastapi.testclient.TestClient`

ERA001 Found commented-out code
   --> tests/conftest.py:194:5
    |
193 |     # Import your FastAPI app here
194 |     # from isa_superapp.api.app import app
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
195 |     # with TestClient(app) as client:
196 |     #     yield client
    |
help: Remove commented-out code

PTH201 [*] Do not pass the current directory explicitly to `Path`
   --> tests/conftest.py:344:26
    |
342 |     ]
343 |     for pattern in test_dirs:
344 |         for path in Path(".").glob(pattern):
    |                          ^^^
345 |             if path.is_file():
346 |                 path.unlink()
    |
help: Remove the current directory argument

F811 [*] Redefinition of unused `os` from line 12
   --> tests/conftest.py:399:12
    |
397 | def performance_monitor() -> Generator[Any, None, None]:
398 |     """Monitor performance during test execution."""
399 |     import os
    |            ^^ `os` redefined here
400 |     import time
    |
   ::: tests/conftest.py:12:8
    |
 10 | import json
 11 | import logging
 12 | import os
    |        -- previous definition of `os` here
 13 | import tempfile
 14 | from pathlib import Path
    |
help: Remove definition: `os`

RUF022 [*] `__all__` is not sorted
   --> tests/conftest.py:446:11
    |
445 |   # Export commonly used fixtures for easy import
446 |   __all__ = [
    |  ___________^
447 | |     "test_env_vars",
448 | |     "mock_openai_client",
449 | |     "mock_anthropic_client",
450 | |     "mock_chroma_client",
451 | |     "mock_redis_client",
452 | |     "test_database",
453 | |     "db_session",
454 | |     "test_client",
455 | |     "mock_vector_store",
456 | |     "mock_cache",
457 | |     "temp_dir",
458 | |     "sample_documents",
459 | |     "sample_query",
460 | |     "performance_benchmark",
461 | |     "mock_exception",
462 | |     "mock_http_error",
463 | |     "app_config",
464 | |     "event_loop",
465 | |     "mock_telemetry",
466 | |     "mock_metrics",
467 | |     "isa_assertions",
468 | |     "performance_monitor",
469 | |     "document_generator",
470 | | ]
    | |_^
    |
help: Apply an isort-style sorting to `__all__`

F401 [*] `typing.Any` imported but unused
 --> tests/test_agents.py:7:20
  |
5 | import asyncio
6 | from datetime import datetime
7 | from typing import Any, Dict, List, Optional, Union
  |                    ^^^
8 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
 --> tests/test_agents.py:7:25
  |
5 | import asyncio
6 | from datetime import datetime
7 | from typing import Any, Dict, List, Optional, Union
  |                         ^^^^
8 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.List` imported but unused
 --> tests/test_agents.py:7:31
  |
5 | import asyncio
6 | from datetime import datetime
7 | from typing import Any, Dict, List, Optional, Union
  |                               ^^^^
8 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
 --> tests/test_agents.py:7:37
  |
5 | import asyncio
6 | from datetime import datetime
7 | from typing import Any, Dict, List, Optional, Union
  |                                     ^^^^^^^^
8 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Union` imported but unused
 --> tests/test_agents.py:7:47
  |
5 | import asyncio
6 | from datetime import datetime
7 | from typing import Any, Dict, List, Optional, Union
  |                                               ^^^^^
8 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `unittest.mock.patch` imported but unused
  --> tests/test_agents.py:8:44
   |
 6 | from datetime import datetime
 7 | from typing import Any, Dict, List, Optional, Union
 8 | from unittest.mock import AsyncMock, Mock, patch
   |                                            ^^^^^
 9 |
10 | import pytest
   |
help: Remove unused import: `unittest.mock.patch`

F401 [*] `isa_superapp.core.exceptions.ConfigurationError` imported but unused
  --> tests/test_agents.py:22:54
   |
20 |     ResearchAgent,
21 | )
22 | from isa_superapp.core.exceptions import AgentError, ConfigurationError
   |                                                      ^^^^^^^^^^^^^^^^^^
   |
help: Remove unused import: `isa_superapp.core.exceptions.ConfigurationError`

F401 [*] `datetime.datetime` imported but unused
 --> tests/test_core.py:7:22
  |
5 | import json
6 | import logging
7 | from datetime import datetime
  |                      ^^^^^^^^
8 | from typing import Any, Dict, List, Optional, Union
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import: `datetime.datetime`

F401 [*] `typing.Any` imported but unused
 --> tests/test_core.py:8:20
  |
6 | import logging
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional, Union
  |                    ^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
 --> tests/test_core.py:8:25
  |
6 | import logging
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional, Union
  |                         ^^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.List` imported but unused
 --> tests/test_core.py:8:31
  |
6 | import logging
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional, Union
  |                               ^^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
 --> tests/test_core.py:8:37
  |
6 | import logging
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional, Union
  |                                     ^^^^^^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Union` imported but unused
 --> tests/test_core.py:8:47
  |
6 | import logging
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional, Union
  |                                               ^^^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `unittest.mock.AsyncMock` imported but unused
  --> tests/test_core.py:9:27
   |
 7 | from datetime import datetime
 8 | from typing import Any, Dict, List, Optional, Union
 9 | from unittest.mock import AsyncMock, Mock, patch
   |                           ^^^^^^^^^
10 |
11 | import pytest
   |
help: Remove unused import

F401 [*] `unittest.mock.Mock` imported but unused
  --> tests/test_core.py:9:38
   |
 7 | from datetime import datetime
 8 | from typing import Any, Dict, List, Optional, Union
 9 | from unittest.mock import AsyncMock, Mock, patch
   |                                      ^^^^
10 |
11 | import pytest
   |
help: Remove unused import

F401 [*] `unittest.mock.patch` imported but unused
  --> tests/test_core.py:9:44
   |
 7 | from datetime import datetime
 8 | from typing import Any, Dict, List, Optional, Union
 9 | from unittest.mock import AsyncMock, Mock, patch
   |                                            ^^^^^
10 |
11 | import pytest
   |
help: Remove unused import

F811 Redefinition of unused `ConfigurationError` from line 13
  --> tests/test_core.py:13:61
   |
11 | import pytest
12 |
13 | from isa_superapp.core.config import Config, ConfigManager, ConfigurationError
   |                                                             ------------------ previous definition of `ConfigurationError` here
14 | from isa_superapp.core.exceptions import (
15 |     AuthenticationError,
16 |     AuthorizationError,
17 |     ConfigurationError,
   |     ^^^^^^^^^^^^^^^^^^ `ConfigurationError` redefined here
18 |     ISAError,
19 |     OrchestrationError,
   |
help: Remove definition: `ConfigurationError`

F401 [*] `isa_superapp.core.metrics.MetricType` imported but unused
  --> tests/test_core.py:24:57
   |
22 | )
23 | from isa_superapp.core.logging_config import get_logger, setup_logging
24 | from isa_superapp.core.metrics import MetricsCollector, MetricType
   |                                                         ^^^^^^^^^^
25 | from isa_superapp.core.security import SecurityManager, decrypt_data, encrypt_data
26 | from isa_superapp.core.validation import validate_config, validate_document
   |
help: Remove unused import: `isa_superapp.core.metrics.MetricType`

PTH123 `open()` should be replaced by `Path.open()`
   --> tests/test_core.py:119:14
    |
117 |         }
118 |
119 |         with open(config_file, "w") as f:
    |              ^^^^
120 |             json.dump(config_data, f)
    |

F401 [*] `json` imported but unused
 --> tests/test_core_app.py:6:8
  |
5 | import asyncio
6 | import json
  |        ^^^^
7 | import tempfile
8 | from pathlib import Path
  |
help: Remove unused import: `json`

F401 [*] `unittest.mock.AsyncMock` imported but unused
  --> tests/test_core_app.py:9:27
   |
 7 | import tempfile
 8 | from pathlib import Path
 9 | from unittest.mock import AsyncMock, Mock, patch
   |                           ^^^^^^^^^
10 |
11 | import pytest
   |
help: Remove unused import

F401 [*] `unittest.mock.Mock` imported but unused
  --> tests/test_core_app.py:9:38
   |
 7 | import tempfile
 8 | from pathlib import Path
 9 | from unittest.mock import AsyncMock, Mock, patch
   |                                      ^^^^
10 |
11 | import pytest
   |
help: Remove unused import

F401 [*] `json` imported but unused
 --> tests/test_llm_providers.py:5:8
  |
3 | """
4 |
5 | import json
  |        ^^^^
6 | from typing import Any, Dict, List
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import: `json`

F401 [*] `typing.Any` imported but unused
 --> tests/test_llm_providers.py:6:20
  |
5 | import json
6 | from typing import Any, Dict, List
  |                    ^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
 --> tests/test_llm_providers.py:6:25
  |
5 | import json
6 | from typing import Any, Dict, List
  |                         ^^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.List` imported but unused
 --> tests/test_llm_providers.py:6:31
  |
5 | import json
6 | from typing import Any, Dict, List
  |                               ^^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `unittest.mock.AsyncMock` imported but unused
 --> tests/test_llm_providers.py:7:27
  |
5 | import json
6 | from typing import Any, Dict, List
7 | from unittest.mock import AsyncMock, Mock, patch
  |                           ^^^^^^^^^
8 |
9 | import pytest
  |
help: Remove unused import: `unittest.mock.AsyncMock`

B007 Loop control variable `i` not used within loop body
   --> tests/test_llm_providers.py:421:13
    |
420 |         # Test multiple generations
421 |         for i in range(3):
    |             ^
422 |             response = await provider.generate("Test prompt")
423 |             assert response in custom_responses
    |
help: Rename unused `i` to `_i`

B007 Loop control variable `i` not used within loop body
   --> tests/test_llm_providers.py:576:13
    |
574 |         start_time = time.time()
575 |
576 |         for i in range(num_requests):
    |             ^
577 |             await provider.chat(messages)
    |
help: Rename unused `i` to `_i`

F401 [*] `asyncio` imported but unused
 --> tests/test_main.py:5:8
  |
3 | """
4 |
5 | import asyncio
  |        ^^^^^^^
6 | import json
7 | from datetime import datetime
  |
help: Remove unused import: `asyncio`

F401 [*] `json` imported but unused
 --> tests/test_main.py:6:8
  |
5 | import asyncio
6 | import json
  |        ^^^^
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional
  |
help: Remove unused import: `json`

F401 [*] `datetime.datetime` imported but unused
 --> tests/test_main.py:7:22
  |
5 | import asyncio
6 | import json
7 | from datetime import datetime
  |                      ^^^^^^^^
8 | from typing import Any, Dict, List, Optional
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import: `datetime.datetime`

F401 [*] `typing.Any` imported but unused
 --> tests/test_main.py:8:20
  |
6 | import json
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional
  |                    ^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
 --> tests/test_main.py:8:25
  |
6 | import json
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional
  |                         ^^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.List` imported but unused
 --> tests/test_main.py:8:31
  |
6 | import json
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional
  |                               ^^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
 --> tests/test_main.py:8:37
  |
6 | import json
7 | from datetime import datetime
8 | from typing import Any, Dict, List, Optional
  |                                     ^^^^^^^^
9 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `isa_superapp.core.exceptions.ISAError` imported but unused
  --> tests/test_main.py:14:62
   |
13 | from isa_superapp.core.config import Config
14 | from isa_superapp.core.exceptions import ConfigurationError, ISAError
   |                                                              ^^^^^^^^
15 | from isa_superapp.main import ISASuperApp, create_app, main
16 | from isa_superapp.orchestrator.base import TaskDefinition, TaskPriority, TaskStatus
   |
help: Remove unused import: `isa_superapp.core.exceptions.ISAError`

F401 [*] `isa_superapp.vector_store.base.VectorDocument` imported but unused
  --> tests/test_main.py:18:44
   |
16 | from isa_superapp.orchestrator.base import TaskDefinition, TaskPriority, TaskStatus
17 | from isa_superapp.retrieval.base import Document, SearchResult
18 | from isa_superapp.vector_store.base import VectorDocument
   |                                            ^^^^^^^^^^^^^^
   |
help: Remove unused import: `isa_superapp.vector_store.base.VectorDocument`

F401 [*] `typing.Any` imported but unused
 --> tests/test_retrieval.py:6:20
  |
5 | from datetime import datetime
6 | from typing import Any, Dict, List, Optional, Union
  |                    ^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
 --> tests/test_retrieval.py:6:25
  |
5 | from datetime import datetime
6 | from typing import Any, Dict, List, Optional, Union
  |                         ^^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.List` imported but unused
 --> tests/test_retrieval.py:6:31
  |
5 | from datetime import datetime
6 | from typing import Any, Dict, List, Optional, Union
  |                               ^^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
 --> tests/test_retrieval.py:6:37
  |
5 | from datetime import datetime
6 | from typing import Any, Dict, List, Optional, Union
  |                                     ^^^^^^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Union` imported but unused
 --> tests/test_retrieval.py:6:47
  |
5 | from datetime import datetime
6 | from typing import Any, Dict, List, Optional, Union
  |                                               ^^^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `numpy` imported but unused
  --> tests/test_retrieval.py:9:17
   |
 7 | from unittest.mock import AsyncMock, Mock, patch
 8 |
 9 | import numpy as np
   |                 ^^
10 | import pytest
   |
help: Remove unused import: `numpy`

F401 [*] `typing.Union` imported but unused
 --> tests/test_vector_store.py:6:47
  |
5 | from datetime import datetime
6 | from typing import Any, Dict, List, Optional, Union
  |                                               ^^^^^
7 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import: `typing.Union`

F841 Local variable `query` is assigned to but never used
   --> tests/test_vector_store.py:698:9
    |
696 |     async def test_search_hybrid(self, hybrid_store):
697 |         """Test hybrid search combining dense and sparse results."""
698 |         query = "machine learning algorithms"
    |         ^^^^^
699 |         query_embedding = [0.1, 0.2, 0.3, 0.4]
    |
help: Remove assignment to unused variable `query`

F401 [*] `typing.Any` imported but unused
 --> tests/test_vector_stores.py:5:20
  |
3 | """
4 |
5 | from typing import Any, Dict, List, Optional
  |                    ^^^
6 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
 --> tests/test_vector_stores.py:5:25
  |
3 | """
4 |
5 | from typing import Any, Dict, List, Optional
  |                         ^^^^
6 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.List` imported but unused
 --> tests/test_vector_stores.py:5:31
  |
3 | """
4 |
5 | from typing import Any, Dict, List, Optional
  |                               ^^^^
6 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
 --> tests/test_vector_stores.py:5:37
  |
3 | """
4 |
5 | from typing import Any, Dict, List, Optional
  |                                     ^^^^^^^^
6 | from unittest.mock import AsyncMock, Mock, patch
  |
help: Remove unused import

F401 [*] `unittest.mock.AsyncMock` imported but unused
 --> tests/test_vector_stores.py:6:27
  |
5 | from typing import Any, Dict, List, Optional
6 | from unittest.mock import AsyncMock, Mock, patch
  |                           ^^^^^^^^^
7 |
8 | import numpy as np
  |
help: Remove unused import: `unittest.mock.AsyncMock`

F401 [*] `isa_superapp.core.exceptions.VectorStoreConnectionError` imported but unused
  --> tests/test_vector_stores.py:11:42
   |
 9 | import pytest
10 |
11 | from isa_superapp.core.exceptions import VectorStoreConnectionError, VectorStoreError
   |                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^
12 | from isa_superapp.vector_stores.base import SearchResult, VectorStore
13 | from isa_superapp.vector_stores.chroma_store import ChromaVectorStore
   |
help: Remove unused import: `isa_superapp.core.exceptions.VectorStoreConnectionError`

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
  --> tests/test_vector_stores.py:72:21
   |
70 |         doc_id = "doc1"
71 |         content = "This is a test document"
72 |         embedding = np.random.rand(384).tolist()
   |                     ^^^^^^^^^^^^^^
73 |         metadata = {"source": "test", "type": "document"}
   |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
  --> tests/test_vector_stores.py:97:34
   |
95 |                     "doc_id": f"doc{i}",
96 |                     "content": f"Document {i} content",
97 |                     "embedding": np.random.rand(384).tolist(),
   |                                  ^^^^^^^^^^^^^^
98 |                     "metadata": {"index": i},
99 |                 }
   |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:214:21
    |
212 |         doc_id = "test_doc"
213 |         content = "Test document content"
214 |         embedding = np.random.rand(384).tolist()
    |                     ^^^^^^^^^^^^^^
215 |         metadata = {"test": True}
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:241:23
    |
239 |             doc_id=doc_id,
240 |             content="Content to delete",
241 |             embedding=np.random.rand(384).tolist(),
    |                       ^^^^^^^^^^^^^^
242 |             metadata={"to_delete": True},
243 |         )
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:264:23
    |
262 |             doc_id=doc_id,
263 |             content=original_content,
264 |             embedding=np.random.rand(384).tolist(),
    |                       ^^^^^^^^^^^^^^
265 |             metadata={"version": 1},
266 |         )
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:270:25
    |
268 |         # Update the document
269 |         new_content = "Updated content"
270 |         new_embedding = np.random.rand(384).tolist()
    |                         ^^^^^^^^^^^^^^
271 |         new_metadata = {"version": 2, "updated": True}
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:294:27
    |
292 |                 doc_id=f"doc{i}",
293 |                 content=f"Document {i}",
294 |                 embedding=np.random.rand(384).tolist(),
    |                           ^^^^^^^^^^^^^^
295 |                 metadata={"index": i},
296 |             )
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:312:27
    |
310 |                 doc_id=f"doc{i}",
311 |                 content=f"Document {i}",
312 |                 embedding=np.random.rand(384).tolist(),
    |                           ^^^^^^^^^^^^^^
313 |             )
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:326:49
    |
324 |         """Test searching an empty collection."""
325 |         results = await memory_store.search(
326 |             query="test query", query_embedding=np.random.rand(384).tolist()
    |                                                 ^^^^^^^^^^^^^^
327 |         )
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:395:21
    |
393 |         doc_id = "doc1"
394 |         content = "Test document"
395 |         embedding = np.random.rand(384).tolist()
    |                     ^^^^^^^^^^^^^^
396 |         metadata = {"source": "test"}
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:411:27
    |
409 |     async def test_search_documents(self, chroma_store):
410 |         """Test searching documents in Chroma."""
411 |         query_embedding = np.random.rand(384).tolist()
    |                           ^^^^^^^^^^^^^^
412 |
413 |         results = await chroma_store.search(
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:435:27
    |
433 |     async def test_search_with_filtering(self, chroma_store):
434 |         """Test searching with metadata filtering."""
435 |         query_embedding = np.random.rand(384).tolist()
    |                           ^^^^^^^^^^^^^^
436 |         filter_dict = {"source": "test"}
    |

F841 Local variable `results` is assigned to but never used
   --> tests/test_vector_stores.py:438:9
    |
436 |         filter_dict = {"source": "test"}
437 |
438 |         results = await chroma_store.search(
    |         ^^^^^^^
439 |             query="test query", query_embedding=query_embedding, filter_dict=filter_dict
440 |         )
    |
help: Remove assignment to unused variable `results`

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:542:21
    |
540 |         doc_id = "doc3"
541 |         content = "New document"
542 |         embedding = np.random.rand(384).tolist()
    |                     ^^^^^^^^^^^^^^
543 |         metadata = {"source": "test"}
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:557:27
    |
555 |     async def test_search_documents(self, faiss_store):
556 |         """Test searching documents in FAISS."""
557 |         query_embedding = np.random.rand(384).tolist()
    |                           ^^^^^^^^^^^^^^
558 |
559 |         results = await faiss_store.search(
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:714:34
    |
712 |                     "doc_id": f"batch_doc_{i}",
713 |                     "content": f"Batch document {i}",
714 |                     "embedding": np.random.rand(384).tolist(),
    |                                  ^^^^^^^^^^^^^^
715 |                     "metadata": {"batch": True, "index": i},
716 |                 }
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:727:27
    |
726 |         # Test search after batch add
727 |         query_embedding = np.random.rand(384).tolist()
    |                           ^^^^^^^^^^^^^^
728 |         results = await memory_store.search(
729 |             query="batch document", query_embedding=query_embedding, limit=5
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:757:34
    |
755 |                     "doc_id": f"perf_doc_{i}",
756 |                     "content": f"Performance test document {i} with some content",
757 |                     "embedding": np.random.rand(384).tolist(),
    |                                  ^^^^^^^^^^^^^^
758 |                     "metadata": {"index": i, "category": f"cat_{i % 10}"},
759 |                 }
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:768:27
    |
767 |         # Test search performance
768 |         query_embedding = np.random.rand(384).tolist()
    |                           ^^^^^^^^^^^^^^
769 |         start_time = time.time()
770 |         results = await store.search(
    |

F841 Local variable `results` is assigned to but never used
   --> tests/test_vector_stores.py:770:9
    |
768 |         query_embedding = np.random.rand(384).tolist()
769 |         start_time = time.time()
770 |         results = await store.search(
    |         ^^^^^^^
771 |             query="performance test", query_embedding=query_embedding, limit=10
772 |         )
    |
help: Remove assignment to unused variable `results`

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:799:26
    |
798 |         # Create documents with known similarity relationships
799 |         base_embedding = np.random.rand(384)
    |                          ^^^^^^^^^^^^^^
800 |
801 |         documents = []
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:805:21
    |
803 |             # Create documents with decreasing similarity to base
804 |             similarity = 1.0 - (i * 0.1)
805 |             noise = np.random.rand(384) * 0.1
    |                     ^^^^^^^^^^^^^^
806 |             embedding = (base_embedding * similarity + noise).tolist()
    |

NPY002 Replace legacy `np.random.rand` call with `np.random.Generator`
   --> tests/test_vector_stores.py:859:23
    |
857 |             doc_id="test_doc",
858 |             content="Test content",
859 |             embedding=np.random.rand(384).tolist(),
    |                       ^^^^^^^^^^^^^^
860 |             metadata={},
861 |         )
    |

F401 [*] `typing.Any` imported but unused
  --> tests/unit/test_llm.py:9:20
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                    ^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
  --> tests/unit/test_llm.py:9:25
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                         ^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.List` imported but unused
  --> tests/unit/test_llm.py:9:31
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                               ^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
  --> tests/unit/test_llm.py:9:37
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                                     ^^^^^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `unittest.mock.AsyncMock` imported but unused
  --> tests/unit/test_llm.py:10:27
   |
 9 | from typing import Any, Dict, List, Optional
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |                           ^^^^^^^^^
11 |
12 | import pytest
   |
help: Remove unused import: `unittest.mock.AsyncMock`

F401 [*] `tests.utils.MockFactory` imported but unused
  --> tests/unit/test_llm.py:14:25
   |
12 | import pytest
13 |
14 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                         ^^^^^^^^^^^
   |
help: Remove unused import

F401 [*] `tests.utils.TestDataGenerator` imported but unused
  --> tests/unit/test_llm.py:14:38
   |
12 | import pytest
13 |
14 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                                      ^^^^^^^^^^^^^^^^^
   |
help: Remove unused import

F401 [*] `tests.utils.TestValidators` imported but unused
  --> tests/unit/test_llm.py:14:57
   |
12 | import pytest
13 |
14 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                                                         ^^^^^^^^^^^^^^
   |
help: Remove unused import

ERA001 Found commented-out code
  --> tests/unit/test_llm.py:67:13
   |
66 |             # Initialize LLM (this would be your actual implementation)
67 |             # llm = LLM(config=mock_model_config)
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
68 |
69 |             # Verify initialization
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_llm.py:72:13
   |
70 |             mock_tokenizer.assert_called_once_with(mock_model_config["model_name"])
71 |             mock_model.assert_called_once_with(mock_model_config["model_name"])
72 |             # assert llm.model == mock_model_instance
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
73 |             # assert llm.tokenizer == mock_tokenizer_instance
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_llm.py:73:13
   |
71 |             mock_model.assert_called_once_with(mock_model_config["model_name"])
72 |             # assert llm.model == mock_model_instance
73 |             # assert llm.tokenizer == mock_tokenizer_instance
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
74 |
75 |     def test_llm_initialization_with_default_config(self):
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_llm.py:89:13
   |
88 |             # Initialize LLM with defaults
89 |             # llm = LLM()
   |             ^^^^^^^^^^^^^
90 |
91 |             # Verify default configuration
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_llm.py:92:13
   |
91 |             # Verify default configuration
92 |             # assert llm.config["temperature"] == 0.7
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
93 |             # assert llm.config["max_tokens"] == 2048
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_llm.py:93:13
   |
91 |             # Verify default configuration
92 |             # assert llm.config["temperature"] == 0.7
93 |             # assert llm.config["max_tokens"] == 2048
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
94 |
95 |     def test_llm_initialization_failure_handling(self):
   |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:103:13
    |
101 |             # Test initialization with failure
102 |             # with pytest.raises(LLMInitializationError):
103 |             #     LLM(model_name="non-existent-model")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
104 |
105 |     def test_llm_configuration_validation(self, mock_model_config):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:112:9
    |
111 |         # with pytest.raises(ConfigurationError):
112 |         #     LLM(config=invalid_config)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
113 |
114 |         # Test invalid max_tokens
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:119:9
    |
118 |         # with pytest.raises(ConfigurationError):
119 |         #     LLM(config=invalid_config)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:145:9
    |
143 |         """Test single text generation."""
144 |         # Generate text
145 |         # response = mock_llm_instance.generate(sample_prompts[0])
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
146 |
147 |         # Verify generation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:149:9
    |
147 |         # Verify generation
148 |         mock_llm_instance.generate.assert_called_once_with(sample_prompts[0])
149 |         # assert isinstance(response, str)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
150 |         # assert len(response) > 0
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:150:9
    |
148 |         mock_llm_instance.generate.assert_called_once_with(sample_prompts[0])
149 |         # assert isinstance(response, str)
150 |         # assert len(response) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
151 |
152 |     def test_batch_text_generation(self, mock_llm_instance, sample_prompts):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:155:9
    |
153 |         """Test batch text generation."""
154 |         # Generate batch
155 |         # responses = mock_llm_instance.generate_batch(sample_prompts)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
156 |
157 |         # Verify batch generation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:159:9
    |
157 |         # Verify batch generation
158 |         mock_llm_instance.generate_batch.assert_called_once_with(sample_prompts)
159 |         # assert len(responses) == len(sample_prompts)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
160 |         # assert all(isinstance(response, str) for response in responses)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:160:9
    |
158 |         mock_llm_instance.generate_batch.assert_called_once_with(sample_prompts)
159 |         # assert len(responses) == len(sample_prompts)
160 |         # assert all(isinstance(response, str) for response in responses)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
161 |
162 |     def test_text_generation_with_parameters(self, mock_llm_instance):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:168:9
    |
167 |         # Generate with parameters
168 |         # response = mock_llm_instance.generate(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
169 |         #     "Test prompt",
170 |         #     **custom_params
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:171:9
    |
169 |         #     "Test prompt",
170 |         #     **custom_params
171 |         # )
    |         ^^^
172 |
173 |         # Verify parameters were used
    |
help: Remove commented-out code

F841 Local variable `system_prompt` is assigned to but never used
   --> tests/unit/test_llm.py:180:9
    |
178 |     def test_text_generation_with_system_prompt(self, mock_llm_instance):
179 |         """Test text generation with system prompt."""
180 |         system_prompt = "You are a helpful assistant."
    |         ^^^^^^^^^^^^^
181 |         user_prompt = "What is 2+2?"
    |
help: Remove assignment to unused variable `system_prompt`

F841 Local variable `user_prompt` is assigned to but never used
   --> tests/unit/test_llm.py:181:9
    |
179 |         """Test text generation with system prompt."""
180 |         system_prompt = "You are a helpful assistant."
181 |         user_prompt = "What is 2+2?"
    |         ^^^^^^^^^^^
182 |
183 |         # Generate with system prompt
    |
help: Remove assignment to unused variable `user_prompt`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:184:9
    |
183 |         # Generate with system prompt
184 |         # response = mock_llm_instance.generate_with_system_prompt(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
185 |         #     user_prompt=user_prompt,
186 |         #     system_prompt=system_prompt
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:185:9
    |
183 |         # Generate with system prompt
184 |         # response = mock_llm_instance.generate_with_system_prompt(
185 |         #     user_prompt=user_prompt,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
186 |         #     system_prompt=system_prompt
187 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:186:9
    |
184 |         # response = mock_llm_instance.generate_with_system_prompt(
185 |         #     user_prompt=user_prompt,
186 |         #     system_prompt=system_prompt
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
187 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:187:9
    |
185 |         #     user_prompt=user_prompt,
186 |         #     system_prompt=system_prompt
187 |         # )
    |         ^^^
188 |
189 |         # Verify system prompt usage
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:190:9
    |
189 |         # Verify system prompt usage
190 |         # assert system_prompt in mock_llm_instance.generate.call_args[0][0]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
191 |
192 |     def test_text_generation_streaming(self, mock_llm_instance):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:199:9
    |
198 |         # Generate with streaming
199 |         # stream = mock_llm_instance.generate_stream("Test prompt")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
200 |
201 |         # Verify streaming
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:202:9
    |
201 |         # Verify streaming
202 |         # response_parts = list(stream)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
203 |         # assert response_parts == mock_stream
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:203:9
    |
201 |         # Verify streaming
202 |         # response_parts = list(stream)
203 |         # assert response_parts == mock_stream
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
204 |
205 |     def test_text_generation_with_context(self, mock_llm_instance):
    |
help: Remove commented-out code

F841 Local variable `context` is assigned to but never used
   --> tests/unit/test_llm.py:207:9
    |
205 |     def test_text_generation_with_context(self, mock_llm_instance):
206 |         """Test text generation with context."""
207 |         context = "Previous conversation context here."
    |         ^^^^^^^
208 |         prompt = "Continue the conversation."
    |
help: Remove assignment to unused variable `context`

F841 Local variable `prompt` is assigned to but never used
   --> tests/unit/test_llm.py:208:9
    |
206 |         """Test text generation with context."""
207 |         context = "Previous conversation context here."
208 |         prompt = "Continue the conversation."
    |         ^^^^^^
209 |
210 |         # Generate with context
    |
help: Remove assignment to unused variable `prompt`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:211:9
    |
210 |         # Generate with context
211 |         # response = mock_llm_instance.generate_with_context(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
212 |         #     prompt=prompt,
213 |         #     context=context
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:212:9
    |
210 |         # Generate with context
211 |         # response = mock_llm_instance.generate_with_context(
212 |         #     prompt=prompt,
    |         ^^^^^^^^^^^^^^^^^^^^
213 |         #     context=context
214 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:213:9
    |
211 |         # response = mock_llm_instance.generate_with_context(
212 |         #     prompt=prompt,
213 |         #     context=context
    |         ^^^^^^^^^^^^^^^^^^^^^
214 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:214:9
    |
212 |         #     prompt=prompt,
213 |         #     context=context
214 |         # )
    |         ^^^
215 |
216 |         # Verify context usage
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:217:9
    |
216 |         # Verify context usage
217 |         # assert context in mock_llm_instance.generate.call_args[0][0]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
218 |
219 |     def test_text_generation_token_counting(self, mock_llm_instance):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:225:9
    |
224 |         # Count tokens
225 |         # token_count = mock_llm_instance.get_token_count("Test prompt")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
226 |
227 |         # Verify token counting
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:229:9
    |
227 |         # Verify token counting
228 |         mock_llm_instance.get_token_count.assert_called_once_with("Test prompt")
229 |         # assert token_count == 50
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
230 |
231 |     def test_text_generation_with_stop_sequences(self, mock_llm_instance):
    |
help: Remove commented-out code

F841 Local variable `stop_sequences` is assigned to but never used
   --> tests/unit/test_llm.py:233:9
    |
231 |     def test_text_generation_with_stop_sequences(self, mock_llm_instance):
232 |         """Test text generation with stop sequences."""
233 |         stop_sequences = ["\n", "END", "STOP"]
    |         ^^^^^^^^^^^^^^
234 |
235 |         # Generate with stop sequences
    |
help: Remove assignment to unused variable `stop_sequences`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:236:9
    |
235 |         # Generate with stop sequences
236 |         # response = mock_llm_instance.generate(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
237 |         #     "Test prompt",
238 |         #     stop_sequences=stop_sequences
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:238:9
    |
236 |         # response = mock_llm_instance.generate(
237 |         #     "Test prompt",
238 |         #     stop_sequences=stop_sequences
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
239 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:239:9
    |
237 |         #     "Test prompt",
238 |         #     stop_sequences=stop_sequences
239 |         # )
    |         ^^^
240 |
241 |         # Verify stop sequences
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:242:9
    |
241 |         # Verify stop sequences
242 |         # assert not any(stop in response for stop in stop_sequences)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:286:13
    |
285 |             # Load template
286 |             # template = prompt_manager.load_template("qa_template")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
287 |
288 |             # Verify loading
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:291:13
    |
289 |             mock_open.assert_called_once()
290 |             mock_json_load.assert_called_once()
291 |             # assert template["name"] == "qa_template"
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
292 |
293 |     def test_prompt_template_rendering(self, mock_prompt_template):
    |
help: Remove commented-out code

F841 Local variable `variables` is assigned to but never used
   --> tests/unit/test_llm.py:296:9
    |
294 |         """Test prompt template rendering."""
295 |         # Mock template rendering
296 |         variables = {
    |         ^^^^^^^^^
297 |             "context": "The sky is blue.",
298 |             "question": "What color is the sky?",
    |
help: Remove assignment to unused variable `variables`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:302:9
    |
301 |         # Render template
302 |         # rendered = prompt_manager.render_template(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
303 |         #     template_name="qa_template",
304 |         #     variables=variables
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:303:9
    |
301 |         # Render template
302 |         # rendered = prompt_manager.render_template(
303 |         #     template_name="qa_template",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
304 |         #     variables=variables
305 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:304:9
    |
302 |         # rendered = prompt_manager.render_template(
303 |         #     template_name="qa_template",
304 |         #     variables=variables
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
305 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:305:9
    |
303 |         #     template_name="qa_template",
304 |         #     variables=variables
305 |         # )
    |         ^^^
306 |
307 |         # Verify rendering
    |
help: Remove commented-out code

F841 Local variable `expected` is assigned to but never used
   --> tests/unit/test_llm.py:308:9
    |
307 |         # Verify rendering
308 |         expected = (
    |         ^^^^^^^^
309 |             "Context: The sky is blue.\n\nQuestion: What color is the sky?\n\nAnswer:"
310 |         )
    |
help: Remove assignment to unused variable `expected`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:311:9
    |
309 |             "Context: The sky is blue.\n\nQuestion: What color is the sky?\n\nAnswer:"
310 |         )
311 |         # assert rendered == expected
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
312 |
313 |     def test_prompt_template_validation(self, mock_prompt_template):
    |
help: Remove commented-out code

F841 Local variable `incomplete_variables` is assigned to but never used
   --> tests/unit/test_llm.py:316:9
    |
314 |         """Test prompt template validation."""
315 |         # Test with missing variables
316 |         incomplete_variables = {"context": "Some context"}
    |         ^^^^^^^^^^^^^^^^^^^^
317 |
318 |         # with pytest.raises(TemplateValidationError):
    |
help: Remove assignment to unused variable `incomplete_variables`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:320:9
    |
318 |         # with pytest.raises(TemplateValidationError):
319 |         #     prompt_manager.render_template(
320 |         #         template_name="qa_template",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
321 |         #         variables=incomplete_variables
322 |         #     )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:321:9
    |
319 |         #     prompt_manager.render_template(
320 |         #         template_name="qa_template",
321 |         #         variables=incomplete_variables
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
322 |         #     )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:322:9
    |
320 |         #         template_name="qa_template",
321 |         #         variables=incomplete_variables
322 |         #     )
    |         ^^^^^^^
323 |
324 |         # Test with extra variables (should be allowed)
    |
help: Remove commented-out code

F841 Local variable `extra_variables` is assigned to but never used
   --> tests/unit/test_llm.py:325:9
    |
324 |         # Test with extra variables (should be allowed)
325 |         extra_variables = {
    |         ^^^^^^^^^^^^^^^
326 |             "context": "Context",
327 |             "question": "Question",
    |
help: Remove assignment to unused variable `extra_variables`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:332:9
    |
331 |         # Should not raise error
332 |         # rendered = prompt_manager.render_template(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
333 |         #     template_name="qa_template",
334 |         #     variables=extra_variables
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:333:9
    |
331 |         # Should not raise error
332 |         # rendered = prompt_manager.render_template(
333 |         #     template_name="qa_template",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
334 |         #     variables=extra_variables
335 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:334:9
    |
332 |         # rendered = prompt_manager.render_template(
333 |         #     template_name="qa_template",
334 |         #     variables=extra_variables
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
335 |         # )
336 |         # assert "Context" in rendered
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:335:9
    |
333 |         #     template_name="qa_template",
334 |         #     variables=extra_variables
335 |         # )
    |         ^^^
336 |         # assert "Context" in rendered
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:345:13
    |
344 |             # Load template multiple times
345 |             # template1 = prompt_manager.load_template("summarization")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
346 |             # template2 = prompt_manager.load_template("summarization")
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:346:13
    |
344 |             # Load template multiple times
345 |             # template1 = prompt_manager.load_template("summarization")
346 |             # template2 = prompt_manager.load_template("summarization")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
347 |
348 |             # Verify caching
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:349:13
    |
348 |             # Verify caching
349 |             # assert template1 == template2
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
350 |             # mock_json_load.assert_called_once()  # Should only load once due to caching
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:350:13
    |
348 |             # Verify caching
349 |             # assert template1 == template2
350 |             # mock_json_load.assert_called_once()  # Should only load once due to caching
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
351 |
352 |     def test_dynamic_prompt_generation(self):
    |
help: Remove commented-out code

F841 Local variable `context` is assigned to but never used
   --> tests/unit/test_llm.py:355:9
    |
353 |         """Test dynamic prompt generation."""
354 |         # Mock dynamic prompt generation
355 |         context = "Technical documentation about Python"
    |         ^^^^^^^
356 |         task = "explain decorators"
    |
help: Remove assignment to unused variable `context`

F841 Local variable `task` is assigned to but never used
   --> tests/unit/test_llm.py:356:9
    |
354 |         # Mock dynamic prompt generation
355 |         context = "Technical documentation about Python"
356 |         task = "explain decorators"
    |         ^^^^
357 |
358 |         # Generate dynamic prompt
    |
help: Remove assignment to unused variable `task`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:359:9
    |
358 |         # Generate dynamic prompt
359 |         # prompt = prompt_manager.generate_dynamic_prompt(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
360 |         #     context=context,
361 |         #     task=task,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:360:9
    |
358 |         # Generate dynamic prompt
359 |         # prompt = prompt_manager.generate_dynamic_prompt(
360 |         #     context=context,
    |         ^^^^^^^^^^^^^^^^^^^^^^
361 |         #     task=task,
362 |         #     style="educational",
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:361:9
    |
359 |         # prompt = prompt_manager.generate_dynamic_prompt(
360 |         #     context=context,
361 |         #     task=task,
    |         ^^^^^^^^^^^^^^^^
362 |         #     style="educational",
363 |         #     complexity="intermediate"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:362:9
    |
360 |         #     context=context,
361 |         #     task=task,
362 |         #     style="educational",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
363 |         #     complexity="intermediate"
364 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:363:9
    |
361 |         #     task=task,
362 |         #     style="educational",
363 |         #     complexity="intermediate"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
364 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:364:9
    |
362 |         #     style="educational",
363 |         #     complexity="intermediate"
364 |         # )
    |         ^^^
365 |
366 |         # Verify dynamic generation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:369:9
    |
367 |         # assert "Python" in prompt
368 |         # assert "decorators" in prompt
369 |         # assert "educational" in prompt.lower()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
370 |
371 |     def test_prompt_history_tracking(self):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:379:13
    |
377 |         for i in range(3):
378 |             prompt = f"Test prompt {i}"
379 |             # prompt_manager.track_prompt(prompt)
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
380 |             prompt_history.append(prompt)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:383:9
    |
382 |         # Verify history tracking
383 |         # history = prompt_manager.get_prompt_history()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
384 |         # assert len(history) == 3
385 |         # assert all(prompt in history for prompt in prompt_history)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:384:9
    |
382 |         # Verify history tracking
383 |         # history = prompt_manager.get_prompt_history()
384 |         # assert len(history) == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
385 |         # assert all(prompt in history for prompt in prompt_history)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:385:9
    |
383 |         # history = prompt_manager.get_prompt_history()
384 |         # assert len(history) == 3
385 |         # assert all(prompt in history for prompt in prompt_history)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
386 |
387 |     def test_prompt_optimization(self):
    |
help: Remove commented-out code

F841 Local variable `original_prompt` is assigned to but never used
   --> tests/unit/test_llm.py:390:9
    |
388 |         """Test prompt optimization."""
389 |         # Mock prompt optimization
390 |         original_prompt = "Tell me about Python"
    |         ^^^^^^^^^^^^^^^
391 |
392 |         # Optimize prompt
    |
help: Remove assignment to unused variable `original_prompt`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:393:9
    |
392 |         # Optimize prompt
393 |         # optimized = prompt_manager.optimize_prompt(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
394 |         #     original_prompt,
395 |         #     optimization_type="clarity"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:395:9
    |
393 |         # optimized = prompt_manager.optimize_prompt(
394 |         #     original_prompt,
395 |         #     optimization_type="clarity"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
396 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:396:9
    |
394 |         #     original_prompt,
395 |         #     optimization_type="clarity"
396 |         # )
    |         ^^^
397 |
398 |         # Verify optimization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:399:9
    |
398 |         # Verify optimization
399 |         # assert len(optimized) > len(original_prompt)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
400 |         # assert "Python" in optimized
401 |         # assert optimized != original_prompt
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:401:9
    |
399 |         # assert len(optimized) > len(original_prompt)
400 |         # assert "Python" in optimized
401 |         # assert optimized != original_prompt
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
402 |
403 |     def test_multi_language_prompt_support(self):
    |
help: Remove commented-out code

F841 Local variable `prompts` is assigned to but never used
   --> tests/unit/test_llm.py:406:9
    |
404 |         """Test multi-language prompt support."""
405 |         # Test prompts in different languages
406 |         prompts = {
    |         ^^^^^^^
407 |             "english": "What is machine learning?",
408 |             "spanish": "¿Qué es el aprendizaje automático?",
    |
help: Remove assignment to unused variable `prompts`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:415:9
    |
413 |         # Process each prompt
414 |         # for language, prompt in prompts.items():
415 |         #     processed = prompt_manager.process_multilingual_prompt(prompt, language)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
416 |         #     assert processed is not None
417 |         #     assert len(processed) > 0
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:417:9
    |
415 |         #     processed = prompt_manager.process_multilingual_prompt(prompt, language)
416 |         #     assert processed is not None
417 |         #     assert len(processed) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:451:9
    |
450 |         # Test RAG pipeline
451 |         # response = rag_pipeline(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
452 |         #     query=query,
453 |         #     retriever=mock_retrieval_engine,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:452:9
    |
450 |         # Test RAG pipeline
451 |         # response = rag_pipeline(
452 |         #     query=query,
    |         ^^^^^^^^^^^^^^^^^^
453 |         #     retriever=mock_retrieval_engine,
454 |         #     generator=mock_llm_instance
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:453:9
    |
451 |         # response = rag_pipeline(
452 |         #     query=query,
453 |         #     retriever=mock_retrieval_engine,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
454 |         #     generator=mock_llm_instance
455 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:454:9
    |
452 |         #     query=query,
453 |         #     retriever=mock_retrieval_engine,
454 |         #     generator=mock_llm_instance
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
455 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:455:9
    |
453 |         #     retriever=mock_retrieval_engine,
454 |         #     generator=mock_llm_instance
455 |         # )
    |         ^^^
456 |
457 |         # Verify RAG integration
    |
help: Remove commented-out code

F841 Local variable `query` is assigned to but never used
   --> tests/unit/test_llm.py:463:9
    |
461 |     def test_context_aware_generation(self, mock_llm_instance, mock_vector_store):
462 |         """Test context-aware text generation."""
463 |         query = "Explain machine learning"
    |         ^^^^^
464 |
465 |         # Test context-aware generation
    |
help: Remove assignment to unused variable `query`

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:466:9
    |
465 |         # Test context-aware generation
466 |         # response = generate_with_context(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
467 |         #     query=query,
468 |         #     vector_store=mock_vector_store,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:467:9
    |
465 |         # Test context-aware generation
466 |         # response = generate_with_context(
467 |         #     query=query,
    |         ^^^^^^^^^^^^^^^^^^
468 |         #     vector_store=mock_vector_store,
469 |         #     llm=mock_llm_instance
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:468:9
    |
466 |         # response = generate_with_context(
467 |         #     query=query,
468 |         #     vector_store=mock_vector_store,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
469 |         #     llm=mock_llm_instance
470 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:469:9
    |
467 |         #     query=query,
468 |         #     vector_store=mock_vector_store,
469 |         #     llm=mock_llm_instance
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
470 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:470:9
    |
468 |         #     vector_store=mock_vector_store,
469 |         #     llm=mock_llm_instance
470 |         # )
    |         ^^^
471 |
472 |         # Verify context usage
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:474:9
    |
472 |         # Verify context usage
473 |         mock_vector_store.similarity_search.assert_called_once()
474 |         # assert len(response) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
475 |
476 |     def test_multi_step_reasoning(self, mock_llm_instance):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:486:9
    |
485 |         # Test multi-step reasoning
486 |         # result = multi_step_reasoning(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
487 |         #     prompt="Solve this complex problem",
488 |         #     llm=mock_llm_instance,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:487:9
    |
485 |         # Test multi-step reasoning
486 |         # result = multi_step_reasoning(
487 |         #     prompt="Solve this complex problem",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
488 |         #     llm=mock_llm_instance,
489 |         #     num_steps=3
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:488:9
    |
486 |         # result = multi_step_reasoning(
487 |         #     prompt="Solve this complex problem",
488 |         #     llm=mock_llm_instance,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
489 |         #     num_steps=3
490 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:489:9
    |
487 |         #     prompt="Solve this complex problem",
488 |         #     llm=mock_llm_instance,
489 |         #     num_steps=3
    |         ^^^^^^^^^^^^^^^^^
490 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:490:9
    |
488 |         #     llm=mock_llm_instance,
489 |         #     num_steps=3
490 |         # )
    |         ^^^
491 |
492 |         # Verify multi-step process
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:493:9
    |
492 |         # Verify multi-step process
493 |         # assert mock_llm_instance.generate.call_count == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
494 |         # assert len(result) == 3
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:494:9
    |
492 |         # Verify multi-step process
493 |         # assert mock_llm_instance.generate.call_count == 3
494 |         # assert len(result) == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
495 |
496 |     def test_llm_with_memory_integration(self, mock_llm_instance):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:503:9
    |
502 |         # Test generation with memory
503 |         # response = generate_with_memory(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
504 |         #     prompt="Continue the conversation",
505 |         #     memory=mock_memory,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:504:9
    |
502 |         # Test generation with memory
503 |         # response = generate_with_memory(
504 |         #     prompt="Continue the conversation",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
505 |         #     memory=mock_memory,
506 |         #     llm=mock_llm_instance
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:505:9
    |
503 |         # response = generate_with_memory(
504 |         #     prompt="Continue the conversation",
505 |         #     memory=mock_memory,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
506 |         #     llm=mock_llm_instance
507 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:506:9
    |
504 |         #     prompt="Continue the conversation",
505 |         #     memory=mock_memory,
506 |         #     llm=mock_llm_instance
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
507 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:507:9
    |
505 |         #     memory=mock_memory,
506 |         #     llm=mock_llm_instance
507 |         # )
    |         ^^^
508 |
509 |         # Verify memory integration
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:511:9
    |
509 |         # Verify memory integration
510 |         mock_memory.get_relevant_context.assert_called_once()
511 |         # assert len(response) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
512 |
513 |     def test_llm_with_tool_integration(self, mock_llm_instance):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:520:9
    |
519 |         # Test generation with tools
520 |         # response = generate_with_tools(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
521 |         #     prompt="Use the calculator tool",
522 |         #     tools=[mock_tool],
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:521:9
    |
519 |         # Test generation with tools
520 |         # response = generate_with_tools(
521 |         #     prompt="Use the calculator tool",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
522 |         #     tools=[mock_tool],
523 |         #     llm=mock_llm_instance
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:522:9
    |
520 |         # response = generate_with_tools(
521 |         #     prompt="Use the calculator tool",
522 |         #     tools=[mock_tool],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^
523 |         #     llm=mock_llm_instance
524 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:523:9
    |
521 |         #     prompt="Use the calculator tool",
522 |         #     tools=[mock_tool],
523 |         #     llm=mock_llm_instance
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
524 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:524:9
    |
522 |         #     tools=[mock_tool],
523 |         #     llm=mock_llm_instance
524 |         # )
    |         ^^^
525 |
526 |         # Verify tool integration
    |
help: Remove commented-out code

F821 Undefined name `RateLimitError`
   --> tests/unit/test_llm.py:538:13
    |
536 |         # Mock rate limit error
537 |         mock_llm_instance.generate.side_effect = [
538 |             RateLimitError("Rate limit exceeded"),
    |             ^^^^^^^^^^^^^^
539 |             "Successful response after retry",
540 |         ]
    |

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:543:9
    |
542 |         # Test with rate limit handling
543 |         # response = generate_with_rate_limit_handling(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
544 |         #     prompt="Test prompt",
545 |         #     llm=mock_llm_instance
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:544:9
    |
542 |         # Test with rate limit handling
543 |         # response = generate_with_rate_limit_handling(
544 |         #     prompt="Test prompt",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
545 |         #     llm=mock_llm_instance
546 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:545:9
    |
543 |         # response = generate_with_rate_limit_handling(
544 |         #     prompt="Test prompt",
545 |         #     llm=mock_llm_instance
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
546 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:546:9
    |
544 |         #     prompt="Test prompt",
545 |         #     llm=mock_llm_instance
546 |         # )
    |         ^^^
547 |
548 |         # Verify retry logic
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:549:9
    |
548 |         # Verify retry logic
549 |         # assert mock_llm_instance.generate.call_count == 2
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
550 |         # assert response == "Successful response after retry"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:550:9
    |
548 |         # Verify retry logic
549 |         # assert mock_llm_instance.generate.call_count == 2
550 |         # assert response == "Successful response after retry"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
551 |
552 |     def test_timeout_handling(self, mock_llm_instance):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:560:9
    |
558 |         # with pytest.raises(TimeoutError):
559 |         #     generate_with_timeout_handling(
560 |         #         prompt="Test prompt",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
561 |         #         llm=mock_llm_instance,
562 |         #         timeout=5.0
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:561:9
    |
559 |         #     generate_with_timeout_handling(
560 |         #         prompt="Test prompt",
561 |         #         llm=mock_llm_instance,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
562 |         #         timeout=5.0
563 |         #     )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:562:9
    |
560 |         #         prompt="Test prompt",
561 |         #         llm=mock_llm_instance,
562 |         #         timeout=5.0
    |         ^^^^^^^^^^^^^^^^^^^^^
563 |         #     )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:563:9
    |
561 |         #         llm=mock_llm_instance,
562 |         #         timeout=5.0
563 |         #     )
    |         ^^^^^^^
564 |
565 |     def test_invalid_response_handling(self, mock_llm_instance):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:571:9
    |
570 |         # Test with invalid response handling
571 |         # response = generate_with_validation(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
572 |         #     prompt="Test prompt",
573 |         #     llm=mock_llm_instance,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:572:9
    |
570 |         # Test with invalid response handling
571 |         # response = generate_with_validation(
572 |         #     prompt="Test prompt",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
573 |         #     llm=mock_llm_instance,
574 |         #     validator=lambda x: len(x) > 0
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:573:9
    |
571 |         # response = generate_with_validation(
572 |         #     prompt="Test prompt",
573 |         #     llm=mock_llm_instance,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
574 |         #     validator=lambda x: len(x) > 0
575 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:574:9
    |
572 |         #     prompt="Test prompt",
573 |         #     llm=mock_llm_instance,
574 |         #     validator=lambda x: len(x) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
575 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:575:9
    |
573 |         #     llm=mock_llm_instance,
574 |         #     validator=lambda x: len(x) > 0
575 |         # )
    |         ^^^
576 |
577 |         # Should handle invalid response appropriately
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:578:9
    |
577 |         # Should handle invalid response appropriately
578 |         # assert response is None or response == "Default response"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
579 |
580 |     def test_context_length_handling(self, mock_llm_instance):
    |
help: Remove commented-out code

F821 Undefined name `ContextLengthError`
   --> tests/unit/test_llm.py:583:50
    |
581 |         """Test context length error handling."""
582 |         # Mock context length error
583 |         mock_llm_instance.generate.side_effect = ContextLengthError("Context too long")
    |                                                  ^^^^^^^^^^^^^^^^^^
584 |
585 |         # Test with context length handling
    |

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:586:9
    |
585 |         # Test with context length handling
586 |         # response = generate_with_context_truncation(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
587 |         #     prompt="Very long prompt" * 1000,
588 |         #     llm=mock_llm_instance,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:587:9
    |
585 |         # Test with context length handling
586 |         # response = generate_with_context_truncation(
587 |         #     prompt="Very long prompt" * 1000,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
588 |         #     llm=mock_llm_instance,
589 |         #     max_context_length=2048
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:588:9
    |
586 |         # response = generate_with_context_truncation(
587 |         #     prompt="Very long prompt" * 1000,
588 |         #     llm=mock_llm_instance,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
589 |         #     max_context_length=2048
590 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:589:9
    |
587 |         #     prompt="Very long prompt" * 1000,
588 |         #     llm=mock_llm_instance,
589 |         #     max_context_length=2048
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
590 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:590:9
    |
588 |         #     llm=mock_llm_instance,
589 |         #     max_context_length=2048
590 |         # )
    |         ^^^
591 |
592 |         # Should handle context length appropriately
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:593:9
    |
592 |         # Should handle context length appropriately
593 |         # assert mock_llm_instance.generate.call_count == 1  # Should retry with truncated context
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:607:9
    |
606 |         # Measure generation time
607 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
608 |         #     mock_llm_instance.generate,
609 |         #     "Test prompt"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:610:9
    |
608 |         #     mock_llm_instance.generate,
609 |         #     "Test prompt"
610 |         # )
    |         ^^^
611 |
612 |         # Assert performance requirement
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:622:9
    |
621 |         # Measure batch generation time
622 |         # prompts = ["Prompt"] * 10
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
623 |         # _, execution_time = measure_execution_time(
624 |         #     mock_llm_instance.generate_batch,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:623:9
    |
621 |         # Measure batch generation time
622 |         # prompts = ["Prompt"] * 10
623 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
624 |         #     mock_llm_instance.generate_batch,
625 |         #     prompts
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:626:9
    |
624 |         #     mock_llm_instance.generate_batch,
625 |         #     prompts
626 |         # )
    |         ^^^
627 |
628 |         # Assert performance requirement
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:638:9
    |
637 |         # Measure memory usage
638 |         # memory_before = get_memory_usage()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
639 |         # mock_llm_instance.generate("Test prompt")
640 |         # memory_after = get_memory_usage()
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:639:9
    |
637 |         # Measure memory usage
638 |         # memory_before = get_memory_usage()
639 |         # mock_llm_instance.generate("Test prompt")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
640 |         # memory_after = get_memory_usage()
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:640:9
    |
638 |         # memory_before = get_memory_usage()
639 |         # mock_llm_instance.generate("Test prompt")
640 |         # memory_after = get_memory_usage()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
641 |
642 |         # Verify memory usage
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_llm.py:643:9
    |
642 |         # Verify memory usage
643 |         # memory_increase = memory_after - memory_before
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
644 |         # assert memory_increase < 100 * 1024 * 1024  # Should not increase by more than 100MB
    |
help: Remove commented-out code

F401 [*] `typing.Any` imported but unused
  --> tests/unit/test_memory.py:10:20
   |
 9 | from datetime import datetime, timedelta
10 | from typing import Any, Dict, List, Optional
   |                    ^^^
11 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
  --> tests/unit/test_memory.py:10:25
   |
 9 | from datetime import datetime, timedelta
10 | from typing import Any, Dict, List, Optional
   |                         ^^^^
11 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.List` imported but unused
  --> tests/unit/test_memory.py:10:31
   |
 9 | from datetime import datetime, timedelta
10 | from typing import Any, Dict, List, Optional
   |                               ^^^^
11 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
  --> tests/unit/test_memory.py:10:37
   |
 9 | from datetime import datetime, timedelta
10 | from typing import Any, Dict, List, Optional
   |                                     ^^^^^^^^
11 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `unittest.mock.AsyncMock` imported but unused
  --> tests/unit/test_memory.py:11:27
   |
 9 | from datetime import datetime, timedelta
10 | from typing import Any, Dict, List, Optional
11 | from unittest.mock import AsyncMock, MagicMock, patch
   |                           ^^^^^^^^^
12 |
13 | import pytest
   |
help: Remove unused import

F401 [*] `unittest.mock.patch` imported but unused
  --> tests/unit/test_memory.py:11:49
   |
 9 | from datetime import datetime, timedelta
10 | from typing import Any, Dict, List, Optional
11 | from unittest.mock import AsyncMock, MagicMock, patch
   |                                                 ^^^^^
12 |
13 | import pytest
   |
help: Remove unused import

F401 [*] `tests.utils.MockFactory` imported but unused
  --> tests/unit/test_memory.py:15:25
   |
13 | import pytest
14 |
15 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                         ^^^^^^^^^^^
   |
help: Remove unused import

F401 [*] `tests.utils.TestValidators` imported but unused
  --> tests/unit/test_memory.py:15:57
   |
13 | import pytest
14 |
15 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                                                         ^^^^^^^^^^^^^^
   |
help: Remove unused import

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:49:9
   |
47 |         """Test conversation memory initialization."""
48 |         # Initialize conversation memory
49 |         # memory = ConversationMemory(store=mock_conversation_store)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
50 |
51 |         # Verify initialization
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:52:9
   |
51 |         # Verify initialization
52 |         # assert memory.store == mock_conversation_store
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
53 |         # assert memory.max_history_length == 100  # Default value
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:53:9
   |
51 |         # Verify initialization
52 |         # assert memory.store == mock_conversation_store
53 |         # assert memory.max_history_length == 100  # Default value
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
54 |
55 |     def test_conversation_memory_with_custom_config(self, mock_conversation_store):
   |
help: Remove commented-out code

F841 Local variable `custom_config` is assigned to but never used
  --> tests/unit/test_memory.py:57:9
   |
55 |     def test_conversation_memory_with_custom_config(self, mock_conversation_store):
56 |         """Test conversation memory with custom configuration."""
57 |         custom_config = {
   |         ^^^^^^^^^^^^^
58 |             "max_history_length": 50,
59 |             "memory_window": 10,
   |
help: Remove assignment to unused variable `custom_config`

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:64:9
   |
63 |         # Initialize with custom config
64 |         # memory = ConversationMemory(
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
65 |         #     store=mock_conversation_store,
66 |         #     config=custom_config
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:65:9
   |
63 |         # Initialize with custom config
64 |         # memory = ConversationMemory(
65 |         #     store=mock_conversation_store,
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
66 |         #     config=custom_config
67 |         # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:66:9
   |
64 |         # memory = ConversationMemory(
65 |         #     store=mock_conversation_store,
66 |         #     config=custom_config
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
67 |         # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:67:9
   |
65 |         #     store=mock_conversation_store,
66 |         #     config=custom_config
67 |         # )
   |         ^^^
68 |
69 |         # Verify custom configuration
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:70:9
   |
69 |         # Verify custom configuration
70 |         # assert memory.max_history_length == 50
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
71 |         # assert memory.memory_window == 10
72 |         # assert memory.summarization_threshold == 20
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:71:9
   |
69 |         # Verify custom configuration
70 |         # assert memory.max_history_length == 50
71 |         # assert memory.memory_window == 10
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
72 |         # assert memory.summarization_threshold == 20
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:72:9
   |
70 |         # assert memory.max_history_length == 50
71 |         # assert memory.memory_window == 10
72 |         # assert memory.summarization_threshold == 20
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
73 |
74 |     def test_add_message_to_conversation(
   |
help: Remove commented-out code

B007 Loop control variable `message` not used within loop body
  --> tests/unit/test_memory.py:79:13
   |
77 |         """Test adding messages to conversation memory."""
78 |         # Add messages
79 |         for message in sample_conversation:
   |             ^^^^^^^
80 |             # memory.add_message(message)
81 |             mock_conversation_store.add_message.assert_called()
   |
help: Rename unused `message` to `_message`

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:80:13
   |
78 |         # Add messages
79 |         for message in sample_conversation:
80 |             # memory.add_message(message)
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
81 |             mock_conversation_store.add_message.assert_called()
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:91:9
   |
90 |         # Get conversation history
91 |         # history = memory.get_conversation_history()
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
92 |
93 |         # Verify history retrieval
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:94:9
   |
93 |         # Verify history retrieval
94 |         # assert len(history) == len(sample_conversation)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
95 |         # assert history == sample_conversation
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_memory.py:95:9
   |
93 |         # Verify history retrieval
94 |         # assert len(history) == len(sample_conversation)
95 |         # assert history == sample_conversation
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
96 |
97 |     def test_get_recent_messages(self, mock_conversation_store, sample_conversation):
   |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:105:9
    |
104 |         # Get recent messages
105 |         # recent = memory.get_recent_messages(count=2)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
106 |
107 |         # Verify recent messages
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:108:9
    |
107 |         # Verify recent messages
108 |         # assert len(recent) == 2
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
109 |         # assert recent == sample_conversation[-2:]
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:109:9
    |
107 |         # Verify recent messages
108 |         # assert len(recent) == 2
109 |         # assert recent == sample_conversation[-2:]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
110 |
111 |     def test_conversation_summarization(self, mock_conversation_store):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:122:9
    |
121 |         # Test summarization
122 |         # summary = memory.summarize_conversation(summarizer=mock_summarizer)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
123 |
124 |         # Verify summarization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:126:9
    |
124 |         # Verify summarization
125 |         mock_summarizer.summarize.assert_called_once()
126 |         # assert summary == "Summary of the conversation"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
127 |
128 |     def test_conversation_context_retrieval(
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:142:9
    |
141 |         # Test context retrieval
142 |         # context = memory.get_relevant_context(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
143 |         #     query="Python features",
144 |         #     retriever=mock_context_retriever
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:143:9
    |
141 |         # Test context retrieval
142 |         # context = memory.get_relevant_context(
143 |         #     query="Python features",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
144 |         #     retriever=mock_context_retriever
145 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:144:9
    |
142 |         # context = memory.get_relevant_context(
143 |         #     query="Python features",
144 |         #     retriever=mock_context_retriever
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
145 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:145:9
    |
143 |         #     query="Python features",
144 |         #     retriever=mock_context_retriever
145 |         # )
    |         ^^^
146 |
147 |         # Verify context retrieval
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:149:9
    |
147 |         # Verify context retrieval
148 |         mock_context_retriever.get_relevant_context.assert_called_once()
149 |         # assert len(context) == 2
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
150 |
151 |     def test_conversation_memory_persistence(self, mock_conversation_store):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:158:9
    |
157 |         # Test persistence
158 |         # memory.save_conversation()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
159 |         # memory.load_conversation()
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:159:9
    |
157 |         # Test persistence
158 |         # memory.save_conversation()
159 |         # memory.load_conversation()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
160 |
161 |         # Verify persistence
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:171:9
    |
170 |         # Test clearing
171 |         # memory.clear_conversation()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
172 |
173 |         # Verify clearing
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:182:9
    |
181 |         # Test concurrent message addition
182 |         # import threading
    |         ^^^^^^^^^^^^^^^^^^
183 |         # threads = []
184 |         # for i in range(5):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:183:9
    |
181 |         # Test concurrent message addition
182 |         # import threading
183 |         # threads = []
    |         ^^^^^^^^^^^^^^
184 |         # for i in range(5):
185 |         #     thread = threading.Thread(
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:185:9
    |
183 |         # threads = []
184 |         # for i in range(5):
185 |         #     thread = threading.Thread(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
186 |         #         target=memory.add_message,
187 |         #         args=({"role": "user", "content": f"Message {i}"},)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:186:9
    |
184 |         # for i in range(5):
185 |         #     thread = threading.Thread(
186 |         #         target=memory.add_message,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
187 |         #         args=({"role": "user", "content": f"Message {i}"},)
188 |         #     )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:187:9
    |
185 |         #     thread = threading.Thread(
186 |         #         target=memory.add_message,
187 |         #         args=({"role": "user", "content": f"Message {i}"},)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
188 |         #     )
189 |         #     threads.append(thread)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:188:9
    |
186 |         #         target=memory.add_message,
187 |         #         args=({"role": "user", "content": f"Message {i}"},)
188 |         #     )
    |         ^^^^^^^
189 |         #     threads.append(thread)
190 |         #     thread.start()
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:189:9
    |
187 |         #         args=({"role": "user", "content": f"Message {i}"},)
188 |         #     )
189 |         #     threads.append(thread)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
190 |         #     thread.start()
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:190:9
    |
188 |         #     )
189 |         #     threads.append(thread)
190 |         #     thread.start()
    |         ^^^^^^^^^^^^^^^^^^^^
191 |
192 |         # for thread in threads:
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:193:9
    |
192 |         # for thread in threads:
193 |         #     thread.join()
    |         ^^^^^^^^^^^^^^^^^^^
194 |
195 |         # Verify thread safety
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:196:9
    |
195 |         # Verify thread safety
196 |         # assert mock_conversation_store.add_message.call_count == 5
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:241:9
    |
239 |         """Test episodic memory initialization."""
240 |         # Initialize episodic memory
241 |         # memory = EpisodicMemory(store=mock_episode_store)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
242 |
243 |         # Verify initialization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:244:9
    |
243 |         # Verify initialization
244 |         # assert memory.store == mock_episode_store
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
245 |         # assert memory.max_episodes == 1000  # Default value
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:245:9
    |
243 |         # Verify initialization
244 |         # assert memory.store == mock_episode_store
245 |         # assert memory.max_episodes == 1000  # Default value
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
246 |
247 |     def test_episode_creation(self, mock_episode_store, sample_episodes):
    |
help: Remove commented-out code

F841 Local variable `episode` is assigned to but never used
   --> tests/unit/test_memory.py:249:9
    |
247 |     def test_episode_creation(self, mock_episode_store, sample_episodes):
248 |         """Test episode creation."""
249 |         episode = sample_episodes[0]
    |         ^^^^^^^
250 |
251 |         # Create episode
    |
help: Remove assignment to unused variable `episode`

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:253:9
    |
251 |         # Create episode
252 |         # memory.add_episode(
253 |         #     event=episode["event"],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
254 |         #     details=episode["details"],
255 |         #     importance=episode["importance"]
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:254:9
    |
252 |         # memory.add_episode(
253 |         #     event=episode["event"],
254 |         #     details=episode["details"],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
255 |         #     importance=episode["importance"]
256 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:255:9
    |
253 |         #     event=episode["event"],
254 |         #     details=episode["details"],
255 |         #     importance=episode["importance"]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
256 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:256:9
    |
254 |         #     details=episode["details"],
255 |         #     importance=episode["importance"]
256 |         # )
    |         ^^^
257 |
258 |         # Verify episode creation
    |
help: Remove commented-out code

F841 Local variable `start_time` is assigned to but never used
   --> tests/unit/test_memory.py:267:9
    |
266 |         # Define time range
267 |         start_time = datetime.now() - timedelta(hours=3)
    |         ^^^^^^^^^^
268 |         end_time = datetime.now()
    |
help: Remove assignment to unused variable `start_time`

F841 Local variable `end_time` is assigned to but never used
   --> tests/unit/test_memory.py:268:9
    |
266 |         # Define time range
267 |         start_time = datetime.now() - timedelta(hours=3)
268 |         end_time = datetime.now()
    |         ^^^^^^^^
269 |
270 |         # Retrieve episodes
    |
help: Remove assignment to unused variable `end_time`

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:271:9
    |
270 |         # Retrieve episodes
271 |         # episodes = memory.get_episodes_by_time_range(start_time, end_time)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
272 |
273 |         # Verify retrieval
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:275:9
    |
273 |         # Verify retrieval
274 |         mock_episode_store.get_episodes.assert_called_once()
275 |         # assert len(episodes) == len(sample_episodes)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
276 |
277 |     def test_episode_search_by_event_type(self, mock_episode_store, sample_episodes):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:285:9
    |
284 |         # Search episodes
285 |         # results = memory.search_episodes(event_type="user_login")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
286 |
287 |         # Verify search
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:291:9
    |
289 |             event_type="user_login"
290 |         )
291 |         # assert len(results) == 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
292 |         # assert results[0]["event"] == "user_login"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:292:9
    |
290 |         )
291 |         # assert len(results) == 1
292 |         # assert results[0]["event"] == "user_login"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
293 |
294 |     def test_episode_importance_scoring(self, mock_episode_store):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:301:9
    |
300 |         # Test importance scoring
301 |         # importance = memory.calculate_episode_importance(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
302 |         #     event="important_event",
303 |         #     details={"critical": True},
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:302:9
    |
300 |         # Test importance scoring
301 |         # importance = memory.calculate_episode_importance(
302 |         #     event="important_event",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
303 |         #     details={"critical": True},
304 |         #     calculator=mock_importance_calculator
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:303:9
    |
301 |         # importance = memory.calculate_episode_importance(
302 |         #     event="important_event",
303 |         #     details={"critical": True},
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
304 |         #     calculator=mock_importance_calculator
305 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:304:9
    |
302 |         #     event="important_event",
303 |         #     details={"critical": True},
304 |         #     calculator=mock_importance_calculator
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
305 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:305:9
    |
303 |         #     details={"critical": True},
304 |         #     calculator=mock_importance_calculator
305 |         # )
    |         ^^^
306 |
307 |         # Verify importance calculation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:309:9
    |
307 |         # Verify importance calculation
308 |         mock_importance_calculator.calculate.assert_called_once()
309 |         # assert importance == 0.75
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
310 |
311 |     def test_episodic_memory_consolidation(self, mock_episode_store, sample_episodes):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:321:9
    |
320 |         # Test consolidation
321 |         # consolidated = memory.consolidate_episodes(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
322 |         #     episodes=sample_episodes,
323 |         #     consolidator=mock_consolidator
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:322:9
    |
320 |         # Test consolidation
321 |         # consolidated = memory.consolidate_episodes(
322 |         #     episodes=sample_episodes,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
323 |         #     consolidator=mock_consolidator
324 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:323:9
    |
321 |         # consolidated = memory.consolidate_episodes(
322 |         #     episodes=sample_episodes,
323 |         #     consolidator=mock_consolidator
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
324 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:324:9
    |
322 |         #     episodes=sample_episodes,
323 |         #     consolidator=mock_consolidator
324 |         # )
    |         ^^^
325 |
326 |         # Verify consolidation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:328:9
    |
326 |         # Verify consolidation
327 |         mock_consolidator.consolidate.assert_called_once()
328 |         # assert consolidated["summary"] == "Consolidated memory"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
329 |
330 |     def test_episodic_memory_forgetting(self, mock_episode_store, sample_episodes):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:338:9
    |
336 |         # Test forgetting
337 |         # memory.apply_forgetting_mechanism(
338 |         #     mechanism=mock_forgetting_mechanism,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
339 |         #     threshold=0.5
340 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:339:9
    |
337 |         # memory.apply_forgetting_mechanism(
338 |         #     mechanism=mock_forgetting_mechanism,
339 |         #     threshold=0.5
    |         ^^^^^^^^^^^^^^^^^^^
340 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:340:9
    |
338 |         #     mechanism=mock_forgetting_mechanism,
339 |         #     threshold=0.5
340 |         # )
    |         ^^^
341 |
342 |         # Verify forgetting
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:357:9
    |
356 |         # Test pattern recognition
357 |         # patterns = memory.recognize_patterns(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
358 |         #     episodes=sample_episodes,
359 |         #     recognizer=mock_pattern_recognizer
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:358:9
    |
356 |         # Test pattern recognition
357 |         # patterns = memory.recognize_patterns(
358 |         #     episodes=sample_episodes,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
359 |         #     recognizer=mock_pattern_recognizer
360 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:359:9
    |
357 |         # patterns = memory.recognize_patterns(
358 |         #     episodes=sample_episodes,
359 |         #     recognizer=mock_pattern_recognizer
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
360 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:360:9
    |
358 |         #     episodes=sample_episodes,
359 |         #     recognizer=mock_pattern_recognizer
360 |         # )
    |         ^^^
361 |
362 |         # Verify pattern recognition
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:364:9
    |
362 |         # Verify pattern recognition
363 |         mock_pattern_recognizer.recognize_patterns.assert_called_once()
364 |         # assert len(patterns) == 2
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
365 |         # assert patterns[0]["pattern"] == "frequent_login"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:365:9
    |
363 |         mock_pattern_recognizer.recognize_patterns.assert_called_once()
364 |         # assert len(patterns) == 2
365 |         # assert patterns[0]["pattern"] == "frequent_login"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:413:9
    |
411 |         """Test semantic memory initialization."""
412 |         # Initialize semantic memory
413 |         # memory = SemanticMemory(store=mock_knowledge_store)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
414 |
415 |         # Verify initialization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:416:9
    |
415 |         # Verify initialization
416 |         # assert memory.store == mock_knowledge_store
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
417 |         # assert memory.confidence_threshold == 0.7  # Default value
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:417:9
    |
415 |         # Verify initialization
416 |         # assert memory.store == mock_knowledge_store
417 |         # assert memory.confidence_threshold == 0.7  # Default value
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
418 |
419 |     def test_knowledge_item_creation(
    |
help: Remove commented-out code

F841 Local variable `item` is assigned to but never used
   --> tests/unit/test_memory.py:423:9
    |
421 |     ):
422 |         """Test knowledge item creation."""
423 |         item = sample_knowledge_items[0]
    |         ^^^^
424 |
425 |         # Create knowledge item
    |
help: Remove assignment to unused variable `item`

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:427:9
    |
425 |         # Create knowledge item
426 |         # memory.add_knowledge(
427 |         #     concept=item["concept"],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
428 |         #     definition=item["definition"],
429 |         #     category=item["category"],
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:428:9
    |
426 |         # memory.add_knowledge(
427 |         #     concept=item["concept"],
428 |         #     definition=item["definition"],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
429 |         #     category=item["category"],
430 |         #     related_concepts=item["related_concepts"],
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:429:9
    |
427 |         #     concept=item["concept"],
428 |         #     definition=item["definition"],
429 |         #     category=item["category"],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
430 |         #     related_concepts=item["related_concepts"],
431 |         #     confidence=item["confidence"]
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:430:9
    |
428 |         #     definition=item["definition"],
429 |         #     category=item["category"],
430 |         #     related_concepts=item["related_concepts"],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
431 |         #     confidence=item["confidence"]
432 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:431:9
    |
429 |         #     category=item["category"],
430 |         #     related_concepts=item["related_concepts"],
431 |         #     confidence=item["confidence"]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
432 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:432:9
    |
430 |         #     related_concepts=item["related_concepts"],
431 |         #     confidence=item["confidence"]
432 |         # )
    |         ^^^
433 |
434 |         # Verify knowledge creation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:445:9
    |
444 |         # Retrieve knowledge
445 |         # knowledge = memory.get_knowledge_by_concept("Python")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
446 |
447 |         # Verify retrieval
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:449:9
    |
447 |         # Verify retrieval
448 |         mock_knowledge_store.get_knowledge.assert_called_once_with("Python")
449 |         # assert len(knowledge) == 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
450 |         # assert knowledge[0]["concept"] == "Python"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:450:9
    |
448 |         mock_knowledge_store.get_knowledge.assert_called_once_with("Python")
449 |         # assert len(knowledge) == 1
450 |         # assert knowledge[0]["concept"] == "Python"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
451 |
452 |     def test_knowledge_search_by_category(
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:462:9
    |
461 |         # Search knowledge
462 |         # results = memory.search_knowledge_by_category("ai")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
463 |
464 |         # Verify search
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:466:9
    |
464 |         # Verify search
465 |         mock_knowledge_store.search_knowledge.assert_called_once_with(category="ai")
466 |         # assert len(results) == 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
467 |         # assert results[0]["concept"] == "Machine Learning"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:467:9
    |
465 |         mock_knowledge_store.search_knowledge.assert_called_once_with(category="ai")
466 |         # assert len(results) == 1
467 |         # assert results[0]["concept"] == "Machine Learning"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
468 |
469 |     def test_knowledge_confidence_scoring(self, mock_knowledge_store):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:476:9
    |
475 |         # Test confidence scoring
476 |         # confidence = memory.calculate_knowledge_confidence(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
477 |         #     concept="New Concept",
478 |         #     evidence=["evidence1", "evidence2"],
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:477:9
    |
475 |         # Test confidence scoring
476 |         # confidence = memory.calculate_knowledge_confidence(
477 |         #     concept="New Concept",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
478 |         #     evidence=["evidence1", "evidence2"],
479 |         #     calculator=mock_confidence_calculator
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:478:9
    |
476 |         # confidence = memory.calculate_knowledge_confidence(
477 |         #     concept="New Concept",
478 |         #     evidence=["evidence1", "evidence2"],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
479 |         #     calculator=mock_confidence_calculator
480 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:479:9
    |
477 |         #     concept="New Concept",
478 |         #     evidence=["evidence1", "evidence2"],
479 |         #     calculator=mock_confidence_calculator
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
480 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:480:9
    |
478 |         #     evidence=["evidence1", "evidence2"],
479 |         #     calculator=mock_confidence_calculator
480 |         # )
    |         ^^^
481 |
482 |         # Verify confidence calculation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:484:9
    |
482 |         # Verify confidence calculation
483 |         mock_confidence_calculator.calculate.assert_called_once()
484 |         # assert confidence == 0.82
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
485 |
486 |     def test_knowledge_inference(self, mock_knowledge_store, sample_knowledge_items):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:497:9
    |
496 |         # Test inference
497 |         # inference = memory.infer_knowledge(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
498 |         #     query="What is deep learning?",
499 |         #     inference_engine=mock_inference_engine
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:498:9
    |
496 |         # Test inference
497 |         # inference = memory.infer_knowledge(
498 |         #     query="What is deep learning?",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
499 |         #     inference_engine=mock_inference_engine
500 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:499:9
    |
497 |         # inference = memory.infer_knowledge(
498 |         #     query="What is deep learning?",
499 |         #     inference_engine=mock_inference_engine
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
500 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:500:9
    |
498 |         #     query="What is deep learning?",
499 |         #     inference_engine=mock_inference_engine
500 |         # )
    |         ^^^
501 |
502 |         # Verify inference
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:504:9
    |
502 |         # Verify inference
503 |         mock_inference_engine.infer.assert_called_once()
504 |         # assert inference["inferred_concept"] == "Deep Learning"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
505 |         # assert inference["confidence"] == 0.75
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:505:9
    |
503 |         mock_inference_engine.infer.assert_called_once()
504 |         # assert inference["inferred_concept"] == "Deep Learning"
505 |         # assert inference["confidence"] == 0.75
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
506 |
507 |     def test_knowledge_consistency_checking(
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:525:9
    |
524 |         # Test consistency checking
525 |         # consistency = memory.check_knowledge_consistency(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
526 |         #     checker=mock_consistency_checker
527 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:526:9
    |
524 |         # Test consistency checking
525 |         # consistency = memory.check_knowledge_consistency(
526 |         #     checker=mock_consistency_checker
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
527 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:527:9
    |
525 |         # consistency = memory.check_knowledge_consistency(
526 |         #     checker=mock_consistency_checker
527 |         # )
    |         ^^^
528 |
529 |         # Verify consistency checking
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:531:9
    |
529 |         # Verify consistency checking
530 |         mock_consistency_checker.check_consistency.assert_called_once()
531 |         # assert not consistency["consistent"]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
532 |         # assert len(consistency["conflicts"]) == 1
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:532:9
    |
530 |         mock_consistency_checker.check_consistency.assert_called_once()
531 |         # assert not consistency["consistent"]
532 |         # assert len(consistency["conflicts"]) == 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:564:9
    |
562 |         """Test memory manager initialization."""
563 |         # Initialize memory manager
564 |         # manager = MemoryManager(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
565 |         #     stores=mock_memory_stores,
566 |         #     config=sample_memory_config
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:565:9
    |
563 |         # Initialize memory manager
564 |         # manager = MemoryManager(
565 |         #     stores=mock_memory_stores,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
566 |         #     config=sample_memory_config
567 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:566:9
    |
564 |         # manager = MemoryManager(
565 |         #     stores=mock_memory_stores,
566 |         #     config=sample_memory_config
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
567 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:567:9
    |
565 |         #     stores=mock_memory_stores,
566 |         #     config=sample_memory_config
567 |         # )
    |         ^^^
568 |
569 |         # Verify initialization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:570:9
    |
569 |         # Verify initialization
570 |         # assert manager.conversation_store == mock_memory_stores["conversation"]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
571 |         # assert manager.episodic_store == mock_memory_stores["episodic"]
572 |         # assert manager.semantic_store == mock_memory_stores["semantic"]
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:571:9
    |
569 |         # Verify initialization
570 |         # assert manager.conversation_store == mock_memory_stores["conversation"]
571 |         # assert manager.episodic_store == mock_memory_stores["episodic"]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
572 |         # assert manager.semantic_store == mock_memory_stores["semantic"]
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:572:9
    |
570 |         # assert manager.conversation_store == mock_memory_stores["conversation"]
571 |         # assert manager.episodic_store == mock_memory_stores["episodic"]
572 |         # assert manager.semantic_store == mock_memory_stores["semantic"]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
573 |
574 |     def test_memory_coordinator_functionality(self, mock_memory_stores):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:585:9
    |
584 |         # Test coordination
585 |         # coordination = memory_manager.coordinate_memory_access(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
586 |         #     query="What do you know about Python?",
587 |         #     coordinator=mock_coordinator
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:586:9
    |
584 |         # Test coordination
585 |         # coordination = memory_manager.coordinate_memory_access(
586 |         #     query="What do you know about Python?",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
587 |         #     coordinator=mock_coordinator
588 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:587:9
    |
585 |         # coordination = memory_manager.coordinate_memory_access(
586 |         #     query="What do you know about Python?",
587 |         #     coordinator=mock_coordinator
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
588 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:588:9
    |
586 |         #     query="What do you know about Python?",
587 |         #     coordinator=mock_coordinator
588 |         # )
    |         ^^^
589 |
590 |         # Verify coordination
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:606:9
    |
605 |         # Test cross-type consolidation
606 |         # consolidation = memory_manager.consolidate_across_memory_types(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
607 |         #     consolidator=mock_consolidator
608 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:607:9
    |
605 |         # Test cross-type consolidation
606 |         # consolidation = memory_manager.consolidate_across_memory_types(
607 |         #     consolidator=mock_consolidator
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
608 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:608:9
    |
606 |         # consolidation = memory_manager.consolidate_across_memory_types(
607 |         #     consolidator=mock_consolidator
608 |         # )
    |         ^^^
609 |
610 |         # Verify consolidation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:612:9
    |
610 |         # Verify consolidation
611 |         mock_consolidator.consolidate_across_types.assert_called_once()
612 |         # assert consolidation["confidence"] == 0.85
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
613 |
614 |     def test_memory_pruning_and_cleanup(self, mock_memory_stores):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:625:9
    |
624 |         # Test pruning
625 |         # pruning_result = memory_manager.prune_memory(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
626 |         #     pruner=mock_pruner,
627 |         #     retention_policy="importance_based"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:626:9
    |
624 |         # Test pruning
625 |         # pruning_result = memory_manager.prune_memory(
626 |         #     pruner=mock_pruner,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
627 |         #     retention_policy="importance_based"
628 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:627:9
    |
625 |         # pruning_result = memory_manager.prune_memory(
626 |         #     pruner=mock_pruner,
627 |         #     retention_policy="importance_based"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
628 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:628:9
    |
626 |         #     pruner=mock_pruner,
627 |         #     retention_policy="importance_based"
628 |         # )
    |         ^^^
629 |
630 |         # Verify pruning
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:632:9
    |
630 |         # Verify pruning
631 |         mock_pruner.prune.assert_called_once()
632 |         # assert pruning_result["pruned_items"] == 50
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
633 |         # assert pruning_result["space_saved"] == "10MB"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:633:9
    |
631 |         mock_pruner.prune.assert_called_once()
632 |         # assert pruning_result["pruned_items"] == 50
633 |         # assert pruning_result["space_saved"] == "10MB"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
634 |
635 |     def test_memory_backup_and_restore(self, mock_memory_stores):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:643:9
    |
642 |         # Test backup
643 |         # backup_path = memory_manager.backup_memory(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
644 |         #     backup_manager=mock_backup_manager
645 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:644:9
    |
642 |         # Test backup
643 |         # backup_path = memory_manager.backup_memory(
644 |         #     backup_manager=mock_backup_manager
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
645 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:645:9
    |
643 |         # backup_path = memory_manager.backup_memory(
644 |         #     backup_manager=mock_backup_manager
645 |         # )
    |         ^^^
646 |
647 |         # Test restore
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:648:9
    |
647 |         # Test restore
648 |         # restore_success = memory_manager.restore_memory(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
649 |         #     backup_path=backup_path,
650 |         #     backup_manager=mock_backup_manager
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:649:9
    |
647 |         # Test restore
648 |         # restore_success = memory_manager.restore_memory(
649 |         #     backup_path=backup_path,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
650 |         #     backup_manager=mock_backup_manager
651 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:650:9
    |
648 |         # restore_success = memory_manager.restore_memory(
649 |         #     backup_path=backup_path,
650 |         #     backup_manager=mock_backup_manager
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
651 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:651:9
    |
649 |         #     backup_path=backup_path,
650 |         #     backup_manager=mock_backup_manager
651 |         # )
    |         ^^^
652 |
653 |         # Verify backup/restore
    |
help: Remove commented-out code

F821 Undefined name `backup_path`
   --> tests/unit/test_memory.py:655:61
    |
653 |         # Verify backup/restore
654 |         mock_backup_manager.backup.assert_called_once()
655 |         mock_backup_manager.restore.assert_called_once_with(backup_path)
    |                                                             ^^^^^^^^^^^
656 |         # assert restore_success
    |

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:671:9
    |
670 |         # Test metrics collection
671 |         # metrics = memory_manager.collect_memory_metrics(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
672 |         #     collector=mock_metrics_collector
673 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:672:9
    |
670 |         # Test metrics collection
671 |         # metrics = memory_manager.collect_memory_metrics(
672 |         #     collector=mock_metrics_collector
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
673 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:673:9
    |
671 |         # metrics = memory_manager.collect_memory_metrics(
672 |         #     collector=mock_metrics_collector
673 |         # )
    |         ^^^
674 |
675 |         # Verify metrics
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:677:9
    |
675 |         # Verify metrics
676 |         mock_metrics_collector.collect_metrics.assert_called_once()
677 |         # assert metrics["total_memory_usage"] == "155MB"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
678 |         # assert metrics["memory_efficiency"] == 0.85
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:678:9
    |
676 |         mock_metrics_collector.collect_metrics.assert_called_once()
677 |         # assert metrics["total_memory_usage"] == "155MB"
678 |         # assert metrics["memory_efficiency"] == 0.85
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

F841 Local variable `mock_memory_context` is assigned to but never used
   --> tests/unit/test_memory.py:705:9
    |
704 |         # Mock memory context
705 |         mock_memory_context = {
    |         ^^^^^^^^^^^^^^^^^^^
706 |             "conversation_history": ["Previous messages"],
707 |             "relevant_episodes": ["Recent events"],
    |
help: Remove assignment to unused variable `mock_memory_context`

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:712:9
    |
711 |         # Test LLM with memory
712 |         # response = generate_with_memory(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
713 |         #     prompt="Continue the conversation",
714 |         #     memory_context=mock_memory_context,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:713:9
    |
711 |         # Test LLM with memory
712 |         # response = generate_with_memory(
713 |         #     prompt="Continue the conversation",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
714 |         #     memory_context=mock_memory_context,
715 |         #     llm=mock_llm
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:714:9
    |
712 |         # response = generate_with_memory(
713 |         #     prompt="Continue the conversation",
714 |         #     memory_context=mock_memory_context,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
715 |         #     llm=mock_llm
716 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:715:9
    |
713 |         #     prompt="Continue the conversation",
714 |         #     memory_context=mock_memory_context,
715 |         #     llm=mock_llm
    |         ^^^^^^^^^^^^^^^^^^
716 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:716:9
    |
714 |         #     memory_context=mock_memory_context,
715 |         #     llm=mock_llm
716 |         # )
    |         ^^^
717 |
718 |         # Verify integration
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:719:9
    |
718 |         # Verify integration
719 |         # assert len(response) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
720 |         # assert "memory context" in mock_llm.generate.call_args[0][0]
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:720:9
    |
718 |         # Verify integration
719 |         # assert len(response) > 0
720 |         # assert "memory context" in mock_llm.generate.call_args[0][0]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:731:9
    |
729 |         """Test memory retrieval performance."""
730 |         # Mock large memory dataset
731 |         # large_conversation = TestDataGenerator.generate_conversation_messages(count=1000)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
732 |         # large_episodes = TestDataGenerator.generate_episodes(count=500)
733 |         # large_knowledge = TestDataGenerator.generate_knowledge_items(count=200)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:732:9
    |
730 |         # Mock large memory dataset
731 |         # large_conversation = TestDataGenerator.generate_conversation_messages(count=1000)
732 |         # large_episodes = TestDataGenerator.generate_episodes(count=500)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
733 |         # large_knowledge = TestDataGenerator.generate_knowledge_items(count=200)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:733:9
    |
731 |         # large_conversation = TestDataGenerator.generate_conversation_messages(count=1000)
732 |         # large_episodes = TestDataGenerator.generate_episodes(count=500)
733 |         # large_knowledge = TestDataGenerator.generate_knowledge_items(count=200)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
734 |
735 |         # Measure retrieval time
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:736:9
    |
735 |         # Measure retrieval time
736 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
737 |         #     memory_manager.retrieve_relevant_memories,
738 |         #     "test query"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:739:9
    |
737 |         #     memory_manager.retrieve_relevant_memories,
738 |         #     "test query"
739 |         # )
    |         ^^^
740 |
741 |         # Assert performance requirement
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:748:9
    |
746 |         """Test memory consolidation performance."""
747 |         # Mock large memory dataset
748 |         # large_dataset = {
    |         ^^^^^^^^^^^^^^^^^^^
749 |         #     "conversations": TestDataGenerator.generate_conversations(count=100),
750 |         #     "episodes": TestDataGenerator.generate_episodes(count=1000),
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:749:9
    |
747 |         # Mock large memory dataset
748 |         # large_dataset = {
749 |         #     "conversations": TestDataGenerator.generate_conversations(count=100),
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
750 |         #     "episodes": TestDataGenerator.generate_episodes(count=1000),
751 |         #     "knowledge": TestDataGenerator.generate_knowledge_items(count=500)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:750:9
    |
748 |         # large_dataset = {
749 |         #     "conversations": TestDataGenerator.generate_conversations(count=100),
750 |         #     "episodes": TestDataGenerator.generate_episodes(count=1000),
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
751 |         #     "knowledge": TestDataGenerator.generate_knowledge_items(count=500)
752 |         # }
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:752:9
    |
750 |         #     "episodes": TestDataGenerator.generate_episodes(count=1000),
751 |         #     "knowledge": TestDataGenerator.generate_knowledge_items(count=500)
752 |         # }
    |         ^^^
753 |
754 |         # Measure consolidation time
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:755:9
    |
754 |         # Measure consolidation time
755 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
756 |         #     memory_manager.consolidate_memories,
757 |         #     large_dataset
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:758:9
    |
756 |         #     memory_manager.consolidate_memories,
757 |         #     large_dataset
758 |         # )
    |         ^^^
759 |
760 |         # Assert performance requirement
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:767:9
    |
765 |         """Test memory storage performance."""
766 |         # Mock large memory batch
767 |         # large_batch = TestDataGenerator.generate_memories(count=1000)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
768 |
769 |         # Measure storage time
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:770:9
    |
769 |         # Measure storage time
770 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
771 |         #     memory_manager.store_memories,
772 |         #     large_batch
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_memory.py:773:9
    |
771 |         #     memory_manager.store_memories,
772 |         #     large_batch
773 |         # )
    |         ^^^
774 |
775 |         # Assert performance requirement
    |
help: Remove commented-out code

F401 [*] `typing.Any` imported but unused
  --> tests/unit/test_retrieval.py:9:20
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                    ^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
  --> tests/unit/test_retrieval.py:9:25
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                         ^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.List` imported but unused
  --> tests/unit/test_retrieval.py:9:31
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                               ^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
  --> tests/unit/test_retrieval.py:9:37
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                                     ^^^^^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `unittest.mock.AsyncMock` imported but unused
  --> tests/unit/test_retrieval.py:10:27
   |
 9 | from typing import Any, Dict, List, Optional
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |                           ^^^^^^^^^
11 |
12 | import pytest
   |
help: Remove unused import

F401 [*] `unittest.mock.patch` imported but unused
  --> tests/unit/test_retrieval.py:10:49
   |
 9 | from typing import Any, Dict, List, Optional
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |                                                 ^^^^^
11 |
12 | import pytest
   |
help: Remove unused import

F401 [*] `tests.utils.MockFactory` imported but unused
  --> tests/unit/test_retrieval.py:14:25
   |
12 | import pytest
13 |
14 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                         ^^^^^^^^^^^
   |
help: Remove unused import

F401 [*] `tests.utils.TestValidators` imported but unused
  --> tests/unit/test_retrieval.py:14:57
   |
12 | import pytest
13 |
14 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                                                         ^^^^^^^^^^^^^^
   |
help: Remove unused import

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:43:9
   |
41 |         """Test retrieval engine initialization."""
42 |         # Initialize retrieval engine (this would be your actual implementation)
43 |         # retrieval_engine = RetrievalEngine(
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
44 |         #     vector_store=mock_vector_store,
45 |         #     reranker=mock_reranker
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:44:9
   |
42 |         # Initialize retrieval engine (this would be your actual implementation)
43 |         # retrieval_engine = RetrievalEngine(
44 |         #     vector_store=mock_vector_store,
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
45 |         #     reranker=mock_reranker
46 |         # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:45:9
   |
43 |         # retrieval_engine = RetrievalEngine(
44 |         #     vector_store=mock_vector_store,
45 |         #     reranker=mock_reranker
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
46 |         # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:46:9
   |
44 |         #     vector_store=mock_vector_store,
45 |         #     reranker=mock_reranker
46 |         # )
   |         ^^^
47 |
48 |         # Verify initialization
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:49:9
   |
48 |         # Verify initialization
49 |         # assert retrieval_engine.vector_store == mock_vector_store
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
50 |         # assert retrieval_engine.reranker == mock_reranker
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:50:9
   |
48 |         # Verify initialization
49 |         # assert retrieval_engine.vector_store == mock_vector_store
50 |         # assert retrieval_engine.reranker == mock_reranker
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
51 |
52 |     def test_vector_search(self, mock_vector_store, sample_queries):
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:61:9
   |
60 |         # Perform vector search
61 |         # results = retrieval_engine.vector_search(sample_queries[0], k=5)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
62 |
63 |         # Verify search
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:67:9
   |
65 |             sample_queries[0], k=5
66 |         )
67 |         # assert len(results) == 5
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
68 |         # assert all(TestValidators.validate_search_result(result) for result in results)
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:68:9
   |
66 |         )
67 |         # assert len(results) == 5
68 |         # assert all(TestValidators.validate_search_result(result) for result in results)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
69 |
70 |     def test_hybrid_search(self, mock_vector_store, sample_queries):
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:84:9
   |
83 |         # Perform hybrid search
84 |         # results = retrieval_engine.hybrid_search(sample_queries[0], k=5)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
85 |
86 |         # Verify both search methods were called
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:91:9
   |
90 |         # Verify results are combined and deduplicated
91 |         # assert len(results) <= 5  # Should not exceed k
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
92 |         # assert all(TestValidators.validate_search_result(result) for result in results)
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_retrieval.py:92:9
   |
90 |         # Verify results are combined and deduplicated
91 |         # assert len(results) <= 5  # Should not exceed k
92 |         # assert all(TestValidators.validate_search_result(result) for result in results)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
93 |
94 |     def test_reranking_functionality(self, mock_reranker, sample_queries):
   |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:108:9
    |
107 |         # Perform reranking
108 |         # reranked = retrieval_engine.rerank(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
109 |         #     query=sample_queries[0],
110 |         #     documents=initial_results
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:109:9
    |
107 |         # Perform reranking
108 |         # reranked = retrieval_engine.rerank(
109 |         #     query=sample_queries[0],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
110 |         #     documents=initial_results
111 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:110:9
    |
108 |         # reranked = retrieval_engine.rerank(
109 |         #     query=sample_queries[0],
110 |         #     documents=initial_results
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
111 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:111:9
    |
109 |         #     query=sample_queries[0],
110 |         #     documents=initial_results
111 |         # )
    |         ^^^
112 |
113 |         # Verify reranking
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:117:9
    |
115 |             query=sample_queries[0], documents=initial_results
116 |         )
117 |         # assert len(reranked) == len(initial_results)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
118 |         # assert reranked[0]["relevance_score"] >= reranked[-1]["relevance_score"]
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:118:9
    |
116 |         )
117 |         # assert len(reranked) == len(initial_results)
118 |         # assert reranked[0]["relevance_score"] >= reranked[-1]["relevance_score"]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
119 |
120 |     def test_context_assembly(self, sample_documents):
    |
help: Remove commented-out code

F841 Local variable `retrieved_docs` is assigned to but never used
   --> tests/unit/test_retrieval.py:123:9
    |
121 |         """Test context assembly from retrieved documents."""
122 |         # Mock retrieved documents
123 |         retrieved_docs = sample_documents[:3]
    |         ^^^^^^^^^^^^^^
124 |
125 |         # Assemble context
    |
help: Remove assignment to unused variable `retrieved_docs`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:126:9
    |
125 |         # Assemble context
126 |         # context = retrieval_engine.assemble_context(retrieved_docs)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
127 |
128 |         # Verify context assembly
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:129:9
    |
128 |         # Verify context assembly
129 |         # assert isinstance(context, str)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
130 |         # assert len(context) > 0
131 |         # assert all(doc.get("content", "") in context for doc in retrieved_docs)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:130:9
    |
128 |         # Verify context assembly
129 |         # assert isinstance(context, str)
130 |         # assert len(context) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
131 |         # assert all(doc.get("content", "") in context for doc in retrieved_docs)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:131:9
    |
129 |         # assert isinstance(context, str)
130 |         # assert len(context) > 0
131 |         # assert all(doc.get("content", "") in context for doc in retrieved_docs)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
132 |
133 |     def test_relevance_scoring(self, sample_queries):
    |
help: Remove commented-out code

F841 Local variable `docs` is assigned to but never used
   --> tests/unit/test_retrieval.py:136:9
    |
134 |         """Test relevance scoring for documents."""
135 |         # Mock documents with varying relevance
136 |         docs = [
    |         ^^^^
137 |             {
138 |                 "content": "Highly relevant content about " + sample_queries[0],
    |
help: Remove assignment to unused variable `docs`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:146:9
    |
145 |         # Score documents
146 |         # scored_docs = retrieval_engine.score_relevance(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
147 |         #     query=sample_queries[0],
148 |         #     documents=docs
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:147:9
    |
145 |         # Score documents
146 |         # scored_docs = retrieval_engine.score_relevance(
147 |         #     query=sample_queries[0],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
148 |         #     documents=docs
149 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:148:9
    |
146 |         # scored_docs = retrieval_engine.score_relevance(
147 |         #     query=sample_queries[0],
148 |         #     documents=docs
    |         ^^^^^^^^^^^^^^^^^^^^
149 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:149:9
    |
147 |         #     query=sample_queries[0],
148 |         #     documents=docs
149 |         # )
    |         ^^^
150 |
151 |         # Verify scoring
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:152:9
    |
151 |         # Verify scoring
152 |         # assert len(scored_docs) == len(docs)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
153 |         # assert scored_docs[0]["relevance_score"] > scored_docs[-1]["relevance_score"]
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:153:9
    |
151 |         # Verify scoring
152 |         # assert len(scored_docs) == len(docs)
153 |         # assert scored_docs[0]["relevance_score"] > scored_docs[-1]["relevance_score"]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
154 |
155 |     def test_query_expansion(self, sample_queries):
    |
help: Remove commented-out code

F841 Local variable `original_query` is assigned to but never used
   --> tests/unit/test_retrieval.py:158:9
    |
156 |         """Test query expansion for better retrieval."""
157 |         # Mock expanded queries
158 |         original_query = sample_queries[0]
    |         ^^^^^^^^^^^^^^
159 |
160 |         # Expand query
    |
help: Remove assignment to unused variable `original_query`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:161:9
    |
160 |         # Expand query
161 |         # expanded_queries = retrieval_engine.expand_query(original_query)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
162 |
163 |         # Verify expansion
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:164:9
    |
163 |         # Verify expansion
164 |         # assert isinstance(expanded_queries, list)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
165 |         # assert len(expanded_queries) > 0
166 |         # assert original_query in expanded_queries
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:165:9
    |
163 |         # Verify expansion
164 |         # assert isinstance(expanded_queries, list)
165 |         # assert len(expanded_queries) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
166 |         # assert original_query in expanded_queries
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:184:9
    |
183 |         # Perform filtered search
184 |         # results = retrieval_engine.search_with_filters(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
185 |         #     query=sample_queries[0],
186 |         #     filters=filters
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:185:9
    |
183 |         # Perform filtered search
184 |         # results = retrieval_engine.search_with_filters(
185 |         #     query=sample_queries[0],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
186 |         #     filters=filters
187 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:186:9
    |
184 |         # results = retrieval_engine.search_with_filters(
185 |         #     query=sample_queries[0],
186 |         #     filters=filters
    |         ^^^^^^^^^^^^^^^^^^^^^
187 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:187:9
    |
185 |         #     query=sample_queries[0],
186 |         #     filters=filters
187 |         # )
    |         ^^^
188 |
189 |         # Verify filtered search
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:193:9
    |
191 |             sample_queries[0], filters=filters
192 |         )
193 |         # assert len(results) == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
194 |         # assert all(TestValidators.validate_search_result(result) for result in results)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:194:9
    |
192 |         )
193 |         # assert len(results) == 3
194 |         # assert all(TestValidators.validate_search_result(result) for result in results)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
195 |
196 |     def test_multi_query_retrieval(self, mock_vector_store, sample_queries):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:206:9
    |
205 |         # Perform multi-query retrieval
206 |         # results = retrieval_engine.multi_query_retrieve(sample_queries[:3])
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
207 |
208 |         # Verify multiple searches were performed
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:209:9
    |
208 |         # Verify multiple searches were performed
209 |         # assert mock_vector_store.similarity_search.call_count == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
210 |         # assert len(results) <= 6  # Should combine and deduplicate
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:210:9
    |
208 |         # Verify multiple searches were performed
209 |         # assert mock_vector_store.similarity_search.call_count == 3
210 |         # assert len(results) <= 6  # Should combine and deduplicate
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
211 |
212 |     def test_retrieval_result_deduplication(self):
    |
help: Remove commented-out code

F841 Local variable `duplicate_results` is assigned to but never used
   --> tests/unit/test_retrieval.py:215:9
    |
213 |         """Test deduplication of retrieval results."""
214 |         # Mock duplicate results
215 |         duplicate_results = [
    |         ^^^^^^^^^^^^^^^^^
216 |             {"id": "doc1", "content": "Content 1", "score": 0.9},
217 |             {"id": "doc2", "content": "Content 2", "score": 0.8},
    |
help: Remove assignment to unused variable `duplicate_results`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:224:9
    |
223 |         # Deduplicate results
224 |         # deduplicated = retrieval_engine.deduplicate_results(duplicate_results)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
225 |
226 |         # Verify deduplication
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:227:9
    |
226 |         # Verify deduplication
227 |         # assert len(deduplicated) == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
228 |         # doc_ids = [doc["id"] for doc in deduplicated]
229 |         # assert len(set(doc_ids)) == 3  # All IDs should be unique
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:228:9
    |
226 |         # Verify deduplication
227 |         # assert len(deduplicated) == 3
228 |         # doc_ids = [doc["id"] for doc in deduplicated]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
229 |         # assert len(set(doc_ids)) == 3  # All IDs should be unique
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:229:9
    |
227 |         # assert len(deduplicated) == 3
228 |         # doc_ids = [doc["id"] for doc in deduplicated]
229 |         # assert len(set(doc_ids)) == 3  # All IDs should be unique
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
230 |
231 |     def test_retrieval_confidence_scoring(self, sample_queries):
    |
help: Remove commented-out code

F841 Local variable `results` is assigned to but never used
   --> tests/unit/test_retrieval.py:234:9
    |
232 |         """Test confidence scoring for retrieval results."""
233 |         # Mock results with scores
234 |         results = TestDataGenerator.generate_search_results(
    |         ^^^^^^^
235 |             query=sample_queries[0], num_results=5
236 |         )
    |
help: Remove assignment to unused variable `results`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:239:9
    |
238 |         # Calculate confidence scores
239 |         # confidence_scores = retrieval_engine.calculate_confidence_scores(results)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
240 |
241 |         # Verify confidence scoring
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:242:9
    |
241 |         # Verify confidence scoring
242 |         # assert len(confidence_scores) == len(results)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
243 |         # assert all(0 <= score <= 1 for score in confidence_scores)
244 |         # assert confidence_scores[0] >= confidence_scores[-1]  # Higher score = higher confidence
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:243:9
    |
241 |         # Verify confidence scoring
242 |         # assert len(confidence_scores) == len(results)
243 |         # assert all(0 <= score <= 1 for score in confidence_scores)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
244 |         # assert confidence_scores[0] >= confidence_scores[-1]  # Higher score = higher confidence
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:244:9
    |
242 |         # assert len(confidence_scores) == len(results)
243 |         # assert all(0 <= score <= 1 for score in confidence_scores)
244 |         # assert confidence_scores[0] >= confidence_scores[-1]  # Higher score = higher confidence
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
245 |
246 |     def test_dynamic_k_selection(self, sample_queries):
    |
help: Remove commented-out code

F841 Local variable `high_quality_results` is assigned to but never used
   --> tests/unit/test_retrieval.py:249:9
    |
247 |         """Test dynamic selection of k based on result quality."""
248 |         # Mock results with varying quality
249 |         high_quality_results = TestDataGenerator.generate_search_results(
    |         ^^^^^^^^^^^^^^^^^^^^
250 |             query=sample_queries[0], num_results=10, min_score=0.7
251 |         )
    |
help: Remove assignment to unused variable `high_quality_results`

F841 Local variable `low_quality_results` is assigned to but never used
   --> tests/unit/test_retrieval.py:252:9
    |
250 |             query=sample_queries[0], num_results=10, min_score=0.7
251 |         )
252 |         low_quality_results = TestDataGenerator.generate_search_results(
    |         ^^^^^^^^^^^^^^^^^^^
253 |             query=sample_queries[0], num_results=10, max_score=0.3
254 |         )
    |
help: Remove assignment to unused variable `low_quality_results`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:257:9
    |
256 |         # Test dynamic k selection
257 |         # k_high = retrieval_engine.select_k(high_quality_results, max_k=10)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
258 |         # k_low = retrieval_engine.select_k(low_quality_results, max_k=10)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:258:9
    |
256 |         # Test dynamic k selection
257 |         # k_high = retrieval_engine.select_k(high_quality_results, max_k=10)
258 |         # k_low = retrieval_engine.select_k(low_quality_results, max_k=10)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
259 |
260 |         # Verify dynamic selection
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:261:9
    |
260 |         # Verify dynamic selection
261 |         # assert k_high >= k_low  # Should return more results for high quality
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
262 |         # assert k_high <= 10
263 |         # assert k_low >= 1  # Should return at least 1 result
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:262:9
    |
260 |         # Verify dynamic selection
261 |         # assert k_high >= k_low  # Should return more results for high quality
262 |         # assert k_high <= 10
    |         ^^^^^^^^^^^^^^^^^^^^^
263 |         # assert k_low >= 1  # Should return at least 1 result
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:263:9
    |
261 |         # assert k_high >= k_low  # Should return more results for high quality
262 |         # assert k_high <= 10
263 |         # assert k_low >= 1  # Should return at least 1 result
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

F841 Local variable `documents` is assigned to but never used
   --> tests/unit/test_retrieval.py:277:9
    |
275 |         """Test cross-encoder based reranking."""
276 |         # Mock documents to rerank
277 |         documents = TestDataGenerator.generate_documents(count=5)
    |         ^^^^^^^^^
278 |
279 |         # Mock cross-encoder scores
    |
help: Remove assignment to unused variable `documents`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:284:9
    |
283 |         # Perform reranking
284 |         # reranked = reranker.rerank(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
285 |         #     query=sample_queries[0],
286 |         #     documents=documents
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:285:9
    |
283 |         # Perform reranking
284 |         # reranked = reranker.rerank(
285 |         #     query=sample_queries[0],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
286 |         #     documents=documents
287 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:286:9
    |
284 |         # reranked = reranker.rerank(
285 |         #     query=sample_queries[0],
286 |         #     documents=documents
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
287 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:287:9
    |
285 |         #     query=sample_queries[0],
286 |         #     documents=documents
287 |         # )
    |         ^^^
288 |
289 |         # Verify reranking
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:291:9
    |
289 |         # Verify reranking
290 |         mock_cross_encoder.predict.assert_called_once()
291 |         # assert len(reranked) == len(documents)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
292 |         # assert reranked[0]["relevance_score"] == max(mock_scores)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:292:9
    |
290 |         mock_cross_encoder.predict.assert_called_once()
291 |         # assert len(reranked) == len(documents)
292 |         # assert reranked[0]["relevance_score"] == max(mock_scores)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
293 |
294 |     def test_reranking_with_query_expansion(self, sample_queries):
    |
help: Remove commented-out code

F841 Local variable `expanded_queries` is assigned to but never used
   --> tests/unit/test_retrieval.py:297:9
    |
295 |         """Test reranking with query expansion."""
296 |         # Mock expanded queries
297 |         expanded_queries = [sample_queries[0], "expanded query 1", "expanded query 2"]
    |         ^^^^^^^^^^^^^^^^
298 |
299 |         # Mock documents
    |
help: Remove assignment to unused variable `expanded_queries`

F841 Local variable `documents` is assigned to but never used
   --> tests/unit/test_retrieval.py:300:9
    |
299 |         # Mock documents
300 |         documents = TestDataGenerator.generate_documents(count=5)
    |         ^^^^^^^^^
301 |
302 |         # Perform reranking with expansion
    |
help: Remove assignment to unused variable `documents`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:303:9
    |
302 |         # Perform reranking with expansion
303 |         # reranked = reranker.rerank_with_expansion(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
304 |         #     queries=expanded_queries,
305 |         #     documents=documents
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:304:9
    |
302 |         # Perform reranking with expansion
303 |         # reranked = reranker.rerank_with_expansion(
304 |         #     queries=expanded_queries,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
305 |         #     documents=documents
306 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:305:9
    |
303 |         # reranked = reranker.rerank_with_expansion(
304 |         #     queries=expanded_queries,
305 |         #     documents=documents
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
306 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:306:9
    |
304 |         #     queries=expanded_queries,
305 |         #     documents=documents
306 |         # )
    |         ^^^
307 |
308 |         # Verify reranking with expansion
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:309:9
    |
308 |         # Verify reranking with expansion
309 |         # assert len(reranked) == len(documents)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
310 |         # assert all("expanded_relevance_score" in doc for doc in reranked)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:310:9
    |
308 |         # Verify reranking with expansion
309 |         # assert len(reranked) == len(documents)
310 |         # assert all("expanded_relevance_score" in doc for doc in reranked)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
311 |
312 |     def test_reranking_threshold_filtering(self, sample_queries):
    |
help: Remove commented-out code

F841 Local variable `documents` is assigned to but never used
   --> tests/unit/test_retrieval.py:315:9
    |
313 |         """Test reranking with threshold filtering."""
314 |         # Mock documents with scores
315 |         documents = [
    |         ^^^^^^^^^
316 |             {"content": "Highly relevant", "score": 0.9},
317 |             {"content": "Moderately relevant", "score": 0.6},
    |
help: Remove assignment to unused variable `documents`

F841 Local variable `threshold` is assigned to but never used
   --> tests/unit/test_retrieval.py:323:9
    |
322 |         # Set threshold
323 |         threshold = 0.5
    |         ^^^^^^^^^
324 |
325 |         # Perform threshold filtering
    |
help: Remove assignment to unused variable `threshold`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:326:9
    |
325 |         # Perform threshold filtering
326 |         # filtered = reranker.filter_by_threshold(documents, threshold)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
327 |
328 |         # Verify filtering
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:329:9
    |
328 |         # Verify filtering
329 |         # assert len(filtered) == 2
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
330 |         # assert all(doc["score"] >= threshold for doc in filtered)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:330:9
    |
328 |         # Verify filtering
329 |         # assert len(filtered) == 2
330 |         # assert all(doc["score"] >= threshold for doc in filtered)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
331 |
332 |     def test_reranking_diversity_promotion(self):
    |
help: Remove commented-out code

F841 Local variable `similar_docs` is assigned to but never used
   --> tests/unit/test_retrieval.py:335:9
    |
333 |         """Test reranking with diversity promotion."""
334 |         # Mock similar documents
335 |         similar_docs = [
    |         ^^^^^^^^^^^^
336 |             {"content": "Document about Python programming", "score": 0.9},
337 |             {"content": "Another Python programming guide", "score": 0.85},
    |
help: Remove assignment to unused variable `similar_docs`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:344:9
    |
343 |         # Perform diversity promotion
344 |         # diverse = reranker.promote_diversity(similar_docs, max_similar=2)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
345 |
346 |         # Verify diversity
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:347:9
    |
346 |         # Verify diversity
347 |         # assert len(diverse) <= len(similar_docs)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
348 |         # Check that not all documents are about the same topic
    |
help: Remove commented-out code

F841 Local variable `retrieved_docs` is assigned to but never used
   --> tests/unit/test_retrieval.py:357:9
    |
355 |         """Test basic context assembly."""
356 |         # Mock retrieved documents
357 |         retrieved_docs = sample_documents[:3]
    |         ^^^^^^^^^^^^^^
358 |
359 |         # Assemble context
    |
help: Remove assignment to unused variable `retrieved_docs`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:360:9
    |
359 |         # Assemble context
360 |         # context = context_assembler.assemble(retrieved_docs)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
361 |
362 |         # Verify assembly
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:363:9
    |
362 |         # Verify assembly
363 |         # assert isinstance(context, str)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
364 |         # assert len(context) > 0
365 |         # assert all(doc.get("content", "") in context for doc in retrieved_docs)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:364:9
    |
362 |         # Verify assembly
363 |         # assert isinstance(context, str)
364 |         # assert len(context) > 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
365 |         # assert all(doc.get("content", "") in context for doc in retrieved_docs)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:365:9
    |
363 |         # assert isinstance(context, str)
364 |         # assert len(context) > 0
365 |         # assert all(doc.get("content", "") in context for doc in retrieved_docs)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
366 |
367 |     def test_context_assembly_with_metadata(self, sample_documents):
    |
help: Remove commented-out code

F841 Local variable `docs_with_metadata` is assigned to but never used
   --> tests/unit/test_retrieval.py:370:9
    |
368 |         """Test context assembly with metadata inclusion."""
369 |         # Mock documents with metadata
370 |         docs_with_metadata = [
    |         ^^^^^^^^^^^^^^^^^^
371 |             {
372 |                 "content": "Content 1",
    |
help: Remove assignment to unused variable `docs_with_metadata`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:382:9
    |
381 |         # Assemble context with metadata
382 |         # context = context_assembler.assemble_with_metadata(docs_with_metadata)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
383 |
384 |         # Verify metadata inclusion
    |
help: Remove commented-out code

F841 Local variable `long_docs` is assigned to but never used
   --> tests/unit/test_retrieval.py:393:9
    |
391 |         """Test context truncation for length limits."""
392 |         # Mock long documents
393 |         long_docs = [
    |         ^^^^^^^^^
394 |             {"content": "Very long content " * 1000},  # Very long content
395 |             {"content": "Another long document " * 1000},
    |
help: Remove assignment to unused variable `long_docs`

F841 Local variable `max_length` is assigned to but never used
   --> tests/unit/test_retrieval.py:399:9
    |
398 |         # Set max length
399 |         max_length = 1000
    |         ^^^^^^^^^^
400 |
401 |         # Assemble context with truncation
    |
help: Remove assignment to unused variable `max_length`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:402:9
    |
401 |         # Assemble context with truncation
402 |         # context = context_assembler.assemble_with_limit(long_docs, max_length)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
403 |
404 |         # Verify truncation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:405:9
    |
404 |         # Verify truncation
405 |         # assert len(context) <= max_length
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
406 |         # assert context.endswith("...")  # Should indicate truncation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:406:9
    |
404 |         # Verify truncation
405 |         # assert len(context) <= max_length
406 |         # assert context.endswith("...")  # Should indicate truncation
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
407 |
408 |     def test_context_chunking(self):
    |
help: Remove commented-out code

F841 Local variable `large_context` is assigned to but never used
   --> tests/unit/test_retrieval.py:411:9
    |
409 |         """Test context chunking for large contexts."""
410 |         # Mock large context
411 |         large_context = "Large context " * 10000
    |         ^^^^^^^^^^^^^
412 |
413 |         # Chunk context
    |
help: Remove assignment to unused variable `large_context`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:414:9
    |
413 |         # Chunk context
414 |         # chunks = context_assembler.chunk_context(large_context, chunk_size=1000)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
415 |
416 |         # Verify chunking
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:417:9
    |
416 |         # Verify chunking
417 |         # assert len(chunks) > 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^
418 |         # assert all(len(chunk) <= 1000 for chunk in chunks)
419 |         # assert "".join(chunks) == large_context  # Should reconstruct original
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:418:9
    |
416 |         # Verify chunking
417 |         # assert len(chunks) > 1
418 |         # assert all(len(chunk) <= 1000 for chunk in chunks)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
419 |         # assert "".join(chunks) == large_context  # Should reconstruct original
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:419:9
    |
417 |         # assert len(chunks) > 1
418 |         # assert all(len(chunk) <= 1000 for chunk in chunks)
419 |         # assert "".join(chunks) == large_context  # Should reconstruct original
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
420 |
421 |     def test_context_relevance_weighting(self, sample_queries):
    |
help: Remove commented-out code

F841 Local variable `scored_docs` is assigned to but never used
   --> tests/unit/test_retrieval.py:424:9
    |
422 |         """Test context assembly with relevance weighting."""
423 |         # Mock documents with relevance scores
424 |         scored_docs = [
    |         ^^^^^^^^^^^
425 |             {"content": "Highly relevant content", "score": 0.9},
426 |             {"content": "Moderately relevant content", "score": 0.6},
    |
help: Remove assignment to unused variable `scored_docs`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:431:9
    |
430 |         # Assemble context with weighting
431 |         # context = context_assembler.assemble_weighted(scored_docs)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
432 |
433 |         # Verify weighting (more relevant content should be emphasized)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:434:9
    |
433 |         # Verify weighting (more relevant content should be emphasized)
434 |         # assert scored_docs[0]["content"] in context
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
435 |         # Context should prioritize higher-scored documents
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:465:9
    |
464 |         # Mock LLM response
465 |         # mock_llm_response = "Generated response based on retrieved context"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
466 |
467 |         # Test RAG pipeline
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:468:9
    |
467 |         # Test RAG pipeline
468 |         # response = rag_pipeline(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
469 |         #     query="test query",
470 |         #     retriever=retrieval_engine,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:469:9
    |
467 |         # Test RAG pipeline
468 |         # response = rag_pipeline(
469 |         #     query="test query",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
470 |         #     retriever=retrieval_engine,
471 |         #     generator=mock_llm
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:470:9
    |
468 |         # response = rag_pipeline(
469 |         #     query="test query",
470 |         #     retriever=retrieval_engine,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
471 |         #     generator=mock_llm
472 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:471:9
    |
469 |         #     query="test query",
470 |         #     retriever=retrieval_engine,
471 |         #     generator=mock_llm
    |         ^^^^^^^^^^^^^^^^^^^^^^^^
472 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:472:9
    |
470 |         #     retriever=retrieval_engine,
471 |         #     generator=mock_llm
472 |         # )
    |         ^^^
473 |
474 |         # Verify integration
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:475:9
    |
474 |         # Verify integration
475 |         # assert "retrieved context" in response.lower()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:491:9
    |
490 |         # Measure retrieval time
491 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
492 |         #     retrieval_engine.search,
493 |         #     "test query"
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:494:9
    |
492 |         #     retrieval_engine.search,
493 |         #     "test query"
494 |         # )
    |         ^^^
495 |
496 |         # Assert performance requirement
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:508:9
    |
507 |         # Measure large-scale retrieval
508 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
509 |         #     retrieval_engine.search,
510 |         #     "test query",
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:511:9
    |
509 |         #     retrieval_engine.search,
510 |         #     "test query",
511 |         #     k=1000
    |         ^^^^^^^^^^^^
512 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:512:9
    |
510 |         #     "test query",
511 |         #     k=1000
512 |         # )
    |         ^^^
513 |
514 |         # Assert performance requirement
    |
help: Remove commented-out code

F841 Local variable `documents` is assigned to but never used
   --> tests/unit/test_retrieval.py:521:9
    |
519 |         """Test reranking performance."""
520 |         # Mock documents to rerank
521 |         documents = TestDataGenerator.generate_documents(count=100)
    |         ^^^^^^^^^
522 |
523 |         # Measure reranking time
    |
help: Remove assignment to unused variable `documents`

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:524:9
    |
523 |         # Measure reranking time
524 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
525 |         #     reranker.rerank,
526 |         #     "test query",
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_retrieval.py:528:9
    |
526 |         #     "test query",
527 |         #     documents
528 |         # )
    |         ^^^
529 |
530 |         # Assert performance requirement
    |
help: Remove commented-out code

F401 [*] `typing.Any` imported but unused
  --> tests/unit/test_vector_store.py:9:20
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                    ^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.Dict` imported but unused
  --> tests/unit/test_vector_store.py:9:25
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                         ^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.List` imported but unused
  --> tests/unit/test_vector_store.py:9:31
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                               ^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `typing.Optional` imported but unused
  --> tests/unit/test_vector_store.py:9:37
   |
 7 | """
 8 |
 9 | from typing import Any, Dict, List, Optional
   |                                     ^^^^^^^^
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import

F401 [*] `unittest.mock.AsyncMock` imported but unused
  --> tests/unit/test_vector_store.py:10:27
   |
 9 | from typing import Any, Dict, List, Optional
10 | from unittest.mock import AsyncMock, MagicMock, patch
   |                           ^^^^^^^^^
11 |
12 | import pytest
   |
help: Remove unused import: `unittest.mock.AsyncMock`

F401 [*] `tests.utils.MockFactory` imported but unused
  --> tests/unit/test_vector_store.py:14:25
   |
12 | import pytest
13 |
14 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                         ^^^^^^^^^^^
   |
help: Remove unused import

F401 [*] `tests.utils.TestValidators` imported but unused
  --> tests/unit/test_vector_store.py:14:57
   |
12 | import pytest
13 |
14 | from tests.utils import MockFactory, TestDataGenerator, TestValidators
   |                                                         ^^^^^^^^^^^^^^
   |
help: Remove unused import

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:47:13
   |
46 |             # Initialize ChromaDB vector store (this would be your actual implementation)
47 |             # vector_store = ChromaVectorStore(
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
48 |             #     collection_name="test_collection",
49 |             #     embedding_function="sentence-transformers/all-MiniLM-L6-v2"
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:48:13
   |
46 |             # Initialize ChromaDB vector store (this would be your actual implementation)
47 |             # vector_store = ChromaVectorStore(
48 |             #     collection_name="test_collection",
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
49 |             #     embedding_function="sentence-transformers/all-MiniLM-L6-v2"
50 |             # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:49:13
   |
47 |             # vector_store = ChromaVectorStore(
48 |             #     collection_name="test_collection",
49 |             #     embedding_function="sentence-transformers/all-MiniLM-L6-v2"
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
50 |             # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:50:13
   |
48 |             #     collection_name="test_collection",
49 |             #     embedding_function="sentence-transformers/all-MiniLM-L6-v2"
50 |             # )
   |             ^^^
51 |
52 |             # Verify initialization
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:55:13
   |
53 |             mock_chroma_class.assert_called_once()
54 |             mock_chroma_client.get_or_create_collection.assert_called_once()
55 |             # assert vector_store.collection == mock_collection
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
56 |
57 |     def test_document_insertion(
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:66:9
   |
64 |         # Insert documents
65 |         # vector_store.add_documents(
66 |         #     documents=sample_documents,
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
67 |         #     embeddings=sample_embeddings
68 |         # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:67:9
   |
65 |         # vector_store.add_documents(
66 |         #     documents=sample_documents,
67 |         #     embeddings=sample_embeddings
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
68 |         # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:68:9
   |
66 |         #     documents=sample_documents,
67 |         #     embeddings=sample_embeddings
68 |         # )
   |         ^^^
69 |
70 |         # Verify insertion
   |
help: Remove commented-out code

F841 Local variable `call_args` is assigned to but never used
  --> tests/unit/test_vector_store.py:72:9
   |
70 |         # Verify insertion
71 |         mock_collection.add.assert_called_once()
72 |         call_args = mock_collection.add.call_args
   |         ^^^^^^^^^
73 |         # assert len(call_args[1]["documents"]) == len(sample_documents)
74 |         # assert len(call_args[1]["embeddings"]) == len(sample_embeddings)
   |
help: Remove assignment to unused variable `call_args`

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:73:9
   |
71 |         mock_collection.add.assert_called_once()
72 |         call_args = mock_collection.add.call_args
73 |         # assert len(call_args[1]["documents"]) == len(sample_documents)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
74 |         # assert len(call_args[1]["embeddings"]) == len(sample_embeddings)
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:74:9
   |
72 |         call_args = mock_collection.add.call_args
73 |         # assert len(call_args[1]["documents"]) == len(sample_documents)
74 |         # assert len(call_args[1]["embeddings"]) == len(sample_embeddings)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
75 |
76 |     def test_similarity_search(self, mock_collection, sample_documents):
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:88:9
   |
87 |         # Perform similarity search
88 |         # results = vector_store.similarity_search(
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
89 |         #     query="test query",
90 |         #     k=3
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:89:9
   |
87 |         # Perform similarity search
88 |         # results = vector_store.similarity_search(
89 |         #     query="test query",
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^
90 |         #     k=3
91 |         # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:90:9
   |
88 |         # results = vector_store.similarity_search(
89 |         #     query="test query",
90 |         #     k=3
   |         ^^^^^^^^^
91 |         # )
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:91:9
   |
89 |         #     query="test query",
90 |         #     k=3
91 |         # )
   |         ^^^
92 |
93 |         # Verify search
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:95:9
   |
93 |         # Verify search
94 |         mock_collection.query.assert_called_once()
95 |         # assert len(results) == 3
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
96 |         # assert all(TestValidators.validate_search_result(result) for result in results)
   |
help: Remove commented-out code

ERA001 Found commented-out code
  --> tests/unit/test_vector_store.py:96:9
   |
94 |         mock_collection.query.assert_called_once()
95 |         # assert len(results) == 3
96 |         # assert all(TestValidators.validate_search_result(result) for result in results)
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
97 |
98 |     def test_search_with_filters(self, mock_collection, sample_documents):
   |
help: Remove commented-out code

F841 Local variable `filters` is assigned to but never used
   --> tests/unit/test_vector_store.py:110:9
    |
109 |         # Define filters
110 |         filters = {"category": "technology", "date": {"$gte": "2023-01-01"}}
    |         ^^^^^^^
111 |
112 |         # Perform filtered search
    |
help: Remove assignment to unused variable `filters`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:113:9
    |
112 |         # Perform filtered search
113 |         # results = vector_store.similarity_search_with_filters(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
114 |         #     query="test query",
115 |         #     k=5,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:114:9
    |
112 |         # Perform filtered search
113 |         # results = vector_store.similarity_search_with_filters(
114 |         #     query="test query",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
115 |         #     k=5,
116 |         #     filters=filters
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:115:9
    |
113 |         # results = vector_store.similarity_search_with_filters(
114 |         #     query="test query",
115 |         #     k=5,
    |         ^^^^^^^^^^
116 |         #     filters=filters
117 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:116:9
    |
114 |         #     query="test query",
115 |         #     k=5,
116 |         #     filters=filters
    |         ^^^^^^^^^^^^^^^^^^^^^
117 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:117:9
    |
115 |         #     k=5,
116 |         #     filters=filters
117 |         # )
    |         ^^^
118 |
119 |         # Verify filtered search
    |
help: Remove commented-out code

F841 Local variable `call_args` is assigned to but never used
   --> tests/unit/test_vector_store.py:121:9
    |
119 |         # Verify filtered search
120 |         mock_collection.query.assert_called_once()
121 |         call_args = mock_collection.query.call_args
    |         ^^^^^^^^^
122 |         # assert "where" in call_args[1]
123 |         # assert len(results) == 1
    |
help: Remove assignment to unused variable `call_args`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:122:9
    |
120 |         mock_collection.query.assert_called_once()
121 |         call_args = mock_collection.query.call_args
122 |         # assert "where" in call_args[1]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
123 |         # assert len(results) == 1
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:123:9
    |
121 |         call_args = mock_collection.query.call_args
122 |         # assert "where" in call_args[1]
123 |         # assert len(results) == 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
124 |
125 |     def test_document_update(self, mock_collection):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:137:9
    |
135 |         # Update document
136 |         # vector_store.update_document(
137 |         #     doc_id=doc_id,
    |         ^^^^^^^^^^^^^^^^^^^^
138 |         #     content=updated_content,
139 |         #     metadata=updated_metadata
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:138:9
    |
136 |         # vector_store.update_document(
137 |         #     doc_id=doc_id,
138 |         #     content=updated_content,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
139 |         #     metadata=updated_metadata
140 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:139:9
    |
137 |         #     doc_id=doc_id,
138 |         #     content=updated_content,
139 |         #     metadata=updated_metadata
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
140 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:140:9
    |
138 |         #     content=updated_content,
139 |         #     metadata=updated_metadata
140 |         # )
    |         ^^^
141 |
142 |         # Verify update
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:156:9
    |
155 |         # Delete documents
156 |         # vector_store.delete_documents(doc_ids=doc_ids)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
157 |
158 |         # Verify deletion
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:172:9
    |
171 |         # Get collection stats
172 |         # stats = vector_store.get_collection_stats()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
173 |
174 |         # Verify stats
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:175:9
    |
174 |         # Verify stats
175 |         # assert stats["document_count"] == 100
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
176 |         # assert stats["sample_documents"] == 2
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:176:9
    |
174 |         # Verify stats
175 |         # assert stats["document_count"] == 100
176 |         # assert stats["sample_documents"] == 2
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
177 |
178 |     def test_batch_operations(
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:187:9
    |
185 |         # Perform batch insertion
186 |         # vector_store.add_documents_batch(
187 |         #     documents=sample_documents,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
188 |         #     embeddings=sample_embeddings,
189 |         #     batch_size=5
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:188:9
    |
186 |         # vector_store.add_documents_batch(
187 |         #     documents=sample_documents,
188 |         #     embeddings=sample_embeddings,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
189 |         #     batch_size=5
190 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:189:9
    |
187 |         #     documents=sample_documents,
188 |         #     embeddings=sample_embeddings,
189 |         #     batch_size=5
    |         ^^^^^^^^^^^^^^^^^^
190 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:190:9
    |
188 |         #     embeddings=sample_embeddings,
189 |         #     batch_size=5
190 |         # )
    |         ^^^
191 |
192 |         # Verify batch processing
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:204:9
    |
203 |         # Generate embeddings
204 |         # embeddings = vector_store.generate_embeddings(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
205 |         #     documents=["doc1", "doc2", "doc3"],
206 |         #     embedding_function=mock_embedding_function
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:205:9
    |
203 |         # Generate embeddings
204 |         # embeddings = vector_store.generate_embeddings(
205 |         #     documents=["doc1", "doc2", "doc3"],
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
206 |         #     embedding_function=mock_embedding_function
207 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:206:9
    |
204 |         # embeddings = vector_store.generate_embeddings(
205 |         #     documents=["doc1", "doc2", "doc3"],
206 |         #     embedding_function=mock_embedding_function
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
207 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:207:9
    |
205 |         #     documents=["doc1", "doc2", "doc3"],
206 |         #     embedding_function=mock_embedding_function
207 |         # )
    |         ^^^
208 |
209 |         # Verify embedding generation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:211:9
    |
209 |         # Verify embedding generation
210 |         mock_embedding_function.assert_called_once()
211 |         # assert len(embeddings) == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
212 |         # assert all(len(emb) == 384 for emb in embeddings)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:212:9
    |
210 |         mock_embedding_function.assert_called_once()
211 |         # assert len(embeddings) == 3
212 |         # assert all(len(emb) == 384 for emb in embeddings)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
213 |
214 |     def test_vector_store_persistence(self, mock_chroma_client, mock_collection):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:220:9
    |
219 |         # Persist vector store
220 |         # vector_store.persist()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^
221 |
222 |         # Verify persistence
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:237:9
    |
236 |         # Perform search with scores
237 |         # results = vector_store.similarity_search_with_scores(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
238 |         #     query="test query",
239 |         #     k=3
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:238:9
    |
236 |         # Perform search with scores
237 |         # results = vector_store.similarity_search_with_scores(
238 |         #     query="test query",
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^
239 |         #     k=3
240 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:239:9
    |
237 |         # results = vector_store.similarity_search_with_scores(
238 |         #     query="test query",
239 |         #     k=3
    |         ^^^^^^^^^
240 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:240:9
    |
238 |         #     query="test query",
239 |         #     k=3
240 |         # )
    |         ^^^
241 |
242 |         # Verify results include scores
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:244:9
    |
242 |         # Verify results include scores
243 |         mock_collection.query.assert_called_once()
244 |         # assert len(results) == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
245 |         # assert all("score" in result for result in results)
246 |         # assert results[0]["score"] <= results[1]["score"]  # Lower distance = higher similarity
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:245:9
    |
243 |         mock_collection.query.assert_called_once()
244 |         # assert len(results) == 3
245 |         # assert all("score" in result for result in results)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
246 |         # assert results[0]["score"] <= results[1]["score"]  # Lower distance = higher similarity
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:246:9
    |
244 |         # assert len(results) == 3
245 |         # assert all("score" in result for result in results)
246 |         # assert results[0]["score"] <= results[1]["score"]  # Lower distance = higher similarity
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:263:13
    |
262 |             # Initialize embedding model (this would be your actual implementation)
263 |             # embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
264 |
265 |             # Verify initialization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:267:13
    |
265 |             # Verify initialization
266 |             mock_model_class.assert_called_once_with("all-MiniLM-L6-v2")
267 |             # assert embedding_model.model == mock_embedding_model
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
268 |
269 |     def test_text_embedding_generation(self, mock_embedding_model):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:278:9
    |
277 |         # Generate embedding
278 |         # embedding = embedding_model.embed_text("This is a test sentence.")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
279 |
280 |         # Verify embedding generation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:282:9
    |
280 |         # Verify embedding generation
281 |         mock_embedding_model.encode.assert_called_once_with("This is a test sentence.")
282 |         # assert len(embedding) == 384
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
283 |         # assert isinstance(embedding, list)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:283:9
    |
281 |         mock_embedding_model.encode.assert_called_once_with("This is a test sentence.")
282 |         # assert len(embedding) == 384
283 |         # assert isinstance(embedding, list)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
284 |
285 |     def test_batch_embedding_generation(self, mock_embedding_model):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:293:9
    |
292 |         # Generate batch embeddings
293 |         # embeddings = embedding_model.embed_texts(texts)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
294 |
295 |         # Verify batch generation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:297:9
    |
295 |         # Verify batch generation
296 |         mock_embedding_model.encode.assert_called_once_with(texts)
297 |         # assert len(embeddings) == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
298 |         # assert all(len(emb) == 384 for emb in embeddings)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:298:9
    |
296 |         mock_embedding_model.encode.assert_called_once_with(texts)
297 |         # assert len(embeddings) == 3
298 |         # assert all(len(emb) == 384 for emb in embeddings)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
299 |
300 |     def test_embedding_similarity_calculation(self):
    |
help: Remove commented-out code

F841 Local variable `embedding1` is assigned to but never used
   --> tests/unit/test_vector_store.py:303:9
    |
301 |         """Test embedding similarity calculation."""
302 |         # Mock embeddings
303 |         embedding1 = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |         ^^^^^^^^^^
304 |         embedding2 = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |
help: Remove assignment to unused variable `embedding1`

F841 Local variable `embedding2` is assigned to but never used
   --> tests/unit/test_vector_store.py:304:9
    |
302 |         # Mock embeddings
303 |         embedding1 = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
304 |         embedding2 = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |         ^^^^^^^^^^
305 |
306 |         # Calculate similarity
    |
help: Remove assignment to unused variable `embedding2`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:307:9
    |
306 |         # Calculate similarity
307 |         # similarity = embedding_model.calculate_similarity(embedding1, embedding2)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
308 |
309 |         # Verify similarity calculation
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:310:9
    |
309 |         # Verify similarity calculation
310 |         # assert 0 <= similarity <= 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
311 |         # assert isinstance(similarity, float)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:311:9
    |
309 |         # Verify similarity calculation
310 |         # assert 0 <= similarity <= 1
311 |         # assert isinstance(similarity, float)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
312 |
313 |     def test_embedding_dimension_consistency(self, mock_embedding_model):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:323:9
    |
322 |         # Generate embeddings
323 |         # emb1 = embedding_model.embed_text("Text 1")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
324 |         # emb2 = embedding_model.embed_text("Text 2")
325 |         # emb3 = embedding_model.embed_text("Text 3")
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:324:9
    |
322 |         # Generate embeddings
323 |         # emb1 = embedding_model.embed_text("Text 1")
324 |         # emb2 = embedding_model.embed_text("Text 2")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
325 |         # emb3 = embedding_model.embed_text("Text 3")
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:325:9
    |
323 |         # emb1 = embedding_model.embed_text("Text 1")
324 |         # emb2 = embedding_model.embed_text("Text 2")
325 |         # emb3 = embedding_model.embed_text("Text 3")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
326 |
327 |         # Verify dimension consistency
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:328:9
    |
327 |         # Verify dimension consistency
328 |         # assert len(emb1) == len(emb3)  # Same model should produce same dimensions
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
329 |         # assert len(emb1) != len(emb2)  # Different models may produce different dimensions
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:329:9
    |
327 |         # Verify dimension consistency
328 |         # assert len(emb1) == len(emb3)  # Same model should produce same dimensions
329 |         # assert len(emb1) != len(emb2)  # Different models may produce different dimensions
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
330 |
331 |     def test_embedding_normalization(self, mock_embedding_model):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:338:9
    |
337 |         # Generate normalized embedding
338 |         # normalized = embedding_model.embed_text("Test", normalize=True)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
339 |
340 |         # Verify normalization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:342:9
    |
340 |         # Verify normalization
341 |         # Calculate magnitude
342 |         # magnitude = sum(x**2 for x in normalized) ** 0.5
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
343 |         # assert abs(magnitude - 1.0) < 0.001  # Should be approximately 1
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:343:9
    |
341 |         # Calculate magnitude
342 |         # magnitude = sum(x**2 for x in normalized) ** 0.5
343 |         # assert abs(magnitude - 1.0) < 0.001  # Should be approximately 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
344 |
345 |     def test_embedding_caching(self, mock_embedding_model):
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:354:9
    |
353 |         # Generate same embedding twice
354 |         # emb1 = embedding_model.embed_text("Test text", use_cache=True)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
355 |         # emb2 = embedding_model.embed_text("Test text", use_cache=True)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:355:9
    |
353 |         # Generate same embedding twice
354 |         # emb1 = embedding_model.embed_text("Test text", use_cache=True)
355 |         # emb2 = embedding_model.embed_text("Test text", use_cache=True)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
356 |
357 |         # Verify caching
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:358:9
    |
357 |         # Verify caching
358 |         # assert emb1 == emb2
    |         ^^^^^^^^^^^^^^^^^^^^^
359 |         # mock_embedding_model.encode.assert_called_once()  # Should only be called once due to caching
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:359:9
    |
357 |         # Verify caching
358 |         # assert emb1 == emb2
359 |         # mock_embedding_model.encode.assert_called_once()  # Should only be called once due to caching
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
360 |
361 |     def test_embedding_model_switching(self):
    |
help: Remove commented-out code

F841 Local variable `mock_model1` is assigned to but never used
   --> tests/unit/test_vector_store.py:364:9
    |
362 |         """Test switching between different embedding models."""
363 |         # Mock multiple models
364 |         mock_model1 = MagicMock()
    |         ^^^^^^^^^^^
365 |         mock_model2 = MagicMock()
    |
help: Remove assignment to unused variable `mock_model1`

F841 Local variable `mock_model2` is assigned to but never used
   --> tests/unit/test_vector_store.py:365:9
    |
363 |         # Mock multiple models
364 |         mock_model1 = MagicMock()
365 |         mock_model2 = MagicMock()
    |         ^^^^^^^^^^^
366 |
367 |         # Switch models
    |
help: Remove assignment to unused variable `mock_model2`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:368:9
    |
367 |         # Switch models
368 |         # embedding_model.switch_model("new-model-name")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
369 |
370 |         # Verify model switching
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:371:9
    |
370 |         # Verify model switching
371 |         # assert embedding_model.model_name == "new-model-name"
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
372 |         # New model should be loaded
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:381:9
    |
380 |         # Generate and validate embedding
381 |         # embedding = embedding_model.embed_text("Test")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
382 |         # is_valid = embedding_model.validate_embedding_quality(embedding)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:382:9
    |
380 |         # Generate and validate embedding
381 |         # embedding = embedding_model.embed_text("Test")
382 |         # is_valid = embedding_model.validate_embedding_quality(embedding)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
383 |
384 |         # Verify validation
    |
help: Remove commented-out code

F841 Local variable `vec1` is assigned to but never used
   --> tests/unit/test_vector_store.py:394:9
    |
392 |         """Test different vector similarity metrics."""
393 |         # Mock vectors
394 |         vec1 = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |         ^^^^
395 |         vec2 = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |
help: Remove assignment to unused variable `vec1`

F841 Local variable `vec2` is assigned to but never used
   --> tests/unit/test_vector_store.py:395:9
    |
393 |         # Mock vectors
394 |         vec1 = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
395 |         vec2 = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |         ^^^^
396 |
397 |         # Test cosine similarity
    |
help: Remove assignment to unused variable `vec2`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:398:9
    |
397 |         # Test cosine similarity
398 |         # cosine_sim = vector_ops.cosine_similarity(vec1, vec2)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
399 |
400 |         # Test Euclidean distance
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:401:9
    |
400 |         # Test Euclidean distance
401 |         # euclidean_dist = vector_ops.euclidean_distance(vec1, vec2)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
402 |
403 |         # Test dot product
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:404:9
    |
403 |         # Test dot product
404 |         # dot_product = vector_ops.dot_product(vec1, vec2)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
405 |
406 |         # Verify metrics
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:407:9
    |
406 |         # Verify metrics
407 |         # assert 0 <= cosine_sim <= 1
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
408 |         # assert euclidean_dist >= 0
409 |         # assert isinstance(dot_product, float)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:408:9
    |
406 |         # Verify metrics
407 |         # assert 0 <= cosine_sim <= 1
408 |         # assert euclidean_dist >= 0
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
409 |         # assert isinstance(dot_product, float)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:409:9
    |
407 |         # assert 0 <= cosine_sim <= 1
408 |         # assert euclidean_dist >= 0
409 |         # assert isinstance(dot_product, float)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
410 |
411 |     def test_vector_normalization(self):
    |
help: Remove commented-out code

F841 Local variable `vector` is assigned to but never used
   --> tests/unit/test_vector_store.py:414:9
    |
412 |         """Test vector normalization operations."""
413 |         # Mock vector
414 |         vector = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |         ^^^^^^
415 |
416 |         # Normalize vector
    |
help: Remove assignment to unused variable `vector`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:417:9
    |
416 |         # Normalize vector
417 |         # normalized = vector_ops.normalize_vector(vector)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
418 |
419 |         # Verify normalization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:420:9
    |
419 |         # Verify normalization
420 |         # magnitude = sum(x**2 for x in normalized) ** 0.5
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
421 |         # assert abs(magnitude - 1.0) < 0.001
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:421:9
    |
419 |         # Verify normalization
420 |         # magnitude = sum(x**2 for x in normalized) ** 0.5
421 |         # assert abs(magnitude - 1.0) < 0.001
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
422 |
423 |     def test_vector_dimensionality_reduction(self):
    |
help: Remove commented-out code

F841 Local variable `high_dim_vector` is assigned to but never used
   --> tests/unit/test_vector_store.py:426:9
    |
424 |         """Test vector dimensionality reduction."""
425 |         # Mock high-dimensional vector
426 |         high_dim_vector = TestDataGenerator.generate_embeddings(count=1, dimension=768)[
    |         ^^^^^^^^^^^^^^^
427 |             0
428 |         ]
    |
help: Remove assignment to unused variable `high_dim_vector`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:431:9
    |
430 |         # Reduce dimensions
431 |         # reduced = vector_ops.reduce_dimensions(high_dim_vector, target_dim=384)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
432 |
433 |         # Verify dimensionality reduction
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:434:9
    |
433 |         # Verify dimensionality reduction
434 |         # assert len(reduced) == 384
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
435 |         # assert len(reduced) < len(high_dim_vector)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:435:9
    |
433 |         # Verify dimensionality reduction
434 |         # assert len(reduced) == 384
435 |         # assert len(reduced) < len(high_dim_vector)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
436 |
437 |     def test_vector_clustering(self):
    |
help: Remove commented-out code

F841 Local variable `vectors` is assigned to but never used
   --> tests/unit/test_vector_store.py:440:9
    |
438 |         """Test vector clustering operations."""
439 |         # Mock multiple vectors
440 |         vectors = TestDataGenerator.generate_embeddings(count=10, dimension=384)
    |         ^^^^^^^
441 |
442 |         # Perform clustering
    |
help: Remove assignment to unused variable `vectors`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:443:9
    |
442 |         # Perform clustering
443 |         # clusters = vector_ops.cluster_vectors(vectors, n_clusters=3)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
444 |
445 |         # Verify clustering
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:446:9
    |
445 |         # Verify clustering
446 |         # assert len(clusters) == 3
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
447 |         # assert all(0 <= label < 3 for label in clusters)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:447:9
    |
445 |         # Verify clustering
446 |         # assert len(clusters) == 3
447 |         # assert all(0 <= label < 3 for label in clusters)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
448 |
449 |     def test_vector_quantization(self):
    |
help: Remove commented-out code

F841 Local variable `vector` is assigned to but never used
   --> tests/unit/test_vector_store.py:452:9
    |
450 |         """Test vector quantization for storage optimization."""
451 |         # Mock vector
452 |         vector = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |         ^^^^^^
453 |
454 |         # Quantize vector
    |
help: Remove assignment to unused variable `vector`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:455:9
    |
454 |         # Quantize vector
455 |         # quantized = vector_ops.quantize_vector(vector, bits=8)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
456 |
457 |         # Verify quantization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:458:9
    |
457 |         # Verify quantization
458 |         # assert len(quantized) == len(vector)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
459 |         # assert all(isinstance(x, int) for x in quantized)  # Should be integers
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:459:9
    |
457 |         # Verify quantization
458 |         # assert len(quantized) == len(vector)
459 |         # assert all(isinstance(x, int) for x in quantized)  # Should be integers
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
460 |
461 |     def test_vector_similarity_search_optimization(self):
    |
help: Remove commented-out code

F841 Local variable `query_vec` is assigned to but never used
   --> tests/unit/test_vector_store.py:464:9
    |
462 |         """Test optimized similarity search."""
463 |         # Mock query vector and database vectors
464 |         query_vec = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
    |         ^^^^^^^^^
465 |         db_vectors = TestDataGenerator.generate_embeddings(count=1000, dimension=384)
    |
help: Remove assignment to unused variable `query_vec`

F841 Local variable `db_vectors` is assigned to but never used
   --> tests/unit/test_vector_store.py:465:9
    |
463 |         # Mock query vector and database vectors
464 |         query_vec = TestDataGenerator.generate_embeddings(count=1, dimension=384)[0]
465 |         db_vectors = TestDataGenerator.generate_embeddings(count=1000, dimension=384)
    |         ^^^^^^^^^^
466 |
467 |         # Perform optimized search
    |
help: Remove assignment to unused variable `db_vectors`

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:468:9
    |
467 |         # Perform optimized search
468 |         # results = vector_ops.optimized_similarity_search(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
469 |         #     query_vec,
470 |         #     db_vectors,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:471:9
    |
469 |         #     query_vec,
470 |         #     db_vectors,
471 |         #     k=10
    |         ^^^^^^^^^^
472 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:472:9
    |
470 |         #     db_vectors,
471 |         #     k=10
472 |         # )
    |         ^^^
473 |
474 |         # Verify optimization
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:475:9
    |
474 |         # Verify optimization
475 |         # assert len(results) == 10
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
476 |         # assert all(0 <= score <= 1 for _, score in results)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:476:9
    |
474 |         # Verify optimization
475 |         # assert len(results) == 10
476 |         # assert all(0 <= score <= 1 for _, score in results)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:505:9
    |
504 |         # Test integration with retrieval
505 |         # results = retrieval_engine.search("test query")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
506 |
507 |         # Verify integration
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:508:9
    |
507 |         # Verify integration
508 |         # assert len(results) == 5
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^
509 |         # mock_vector_store.similarity_search.assert_called_once()
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:509:9
    |
507 |         # Verify integration
508 |         # assert len(results) == 5
509 |         # mock_vector_store.similarity_search.assert_called_once()
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:529:9
    |
528 |         # Measure search time
529 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
530 |         #     vector_store.similarity_search,
531 |         #     "test query",
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:532:9
    |
530 |         #     vector_store.similarity_search,
531 |         #     "test query",
532 |         #     k=10
    |         ^^^^^^^^^^
533 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:533:9
    |
531 |         #     "test query",
532 |         #     k=10
533 |         # )
    |         ^^^
534 |
535 |         # Assert performance requirement
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:545:9
    |
544 |         # Generate large batch
545 |         # large_batch = TestDataGenerator.generate_documents(count=1000)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
546 |         # large_embeddings = TestDataGenerator.generate_embeddings(count=1000, dimension=384)
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:546:9
    |
544 |         # Generate large batch
545 |         # large_batch = TestDataGenerator.generate_documents(count=1000)
546 |         # large_embeddings = TestDataGenerator.generate_embeddings(count=1000, dimension=384)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
547 |
548 |         # Measure insertion time
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:549:9
    |
548 |         # Measure insertion time
549 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
550 |         #     vector_store.add_documents_batch,
551 |         #     large_batch,
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:553:9
    |
551 |         #     large_batch,
552 |         #     large_embeddings,
553 |         #     batch_size=100
    |         ^^^^^^^^^^^^^^^^^^^^
554 |         # )
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:554:9
    |
552 |         #     large_embeddings,
553 |         #     batch_size=100
554 |         # )
    |         ^^^
555 |
556 |         # Assert performance requirement
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:569:9
    |
568 |         # Generate embeddings for multiple documents
569 |         # texts = [f"Document {i}" for i in range(100)]
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
570 |
571 |         # Measure generation time
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:572:9
    |
571 |         # Measure generation time
572 |         # _, execution_time = measure_execution_time(
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
573 |         #     embedding_model.embed_texts,
574 |         #     texts
    |
help: Remove commented-out code

ERA001 Found commented-out code
   --> tests/unit/test_vector_store.py:575:9
    |
573 |         #     embedding_model.embed_texts,
574 |         #     texts
575 |         # )
    |         ^^^
576 |
577 |         # Assert performance requirement
    |
help: Remove commented-out code

F401 [*] `typing.Union` imported but unused
  --> tests/utils.py:18:57
   |
16 | from contextlib import contextmanager
17 | from pathlib import Path
18 | from typing import Any, Callable, Dict, List, Optional, Union
   |                                                         ^^^^^
19 | from unittest.mock import AsyncMock, MagicMock, patch
   |
help: Remove unused import: `typing.Union`

F401 [*] `pytest` imported but unused
  --> tests/utils.py:22:8
   |
21 | import numpy as np
22 | import pytest
   |        ^^^^^^
23 | from faker import Faker
   |
help: Remove unused import: `pytest`

NPY002 Replace legacy `np.random.randn` call with `np.random.Generator`
   --> tests/utils.py:111:25
    |
109 |         for _ in range(count):
110 |             # Generate random vector
111 |             embedding = np.random.randn(dimension).tolist()
    |                         ^^^^^^^^^^^^^^^
112 |
113 |             if normalize:
    |

SIM103 Return the negated condition directly
   --> tests/utils.py:310:9
    |
308 |               return False
309 |
310 | /         if "metadata" in document and not isinstance(document["metadata"], dict):
311 | |             return False
312 | |
313 | |         return True
    | |___________________^
314 |
315 |       @staticmethod
    |
help: Inline condition

SIM103 Return the negated condition directly
   --> tests/utils.py:324:9
    |
322 |               return False
323 |
324 | /         if not all(isinstance(x, (int, float)) for x in embedding):
325 | |             return False
326 | |
327 | |         return True
    | |___________________^
328 |
329 |       @staticmethod
    |
help: Inline condition

SIM103 Return the condition `not len(set(lengths)) > 1` directly
   --> tests/utils.py:346:9
    |
344 |           # Check that all lists have the same length
345 |           lengths = [len(result[key]) for key in required_keys]
346 | /         if len(set(lengths)) > 1:
347 | |             return False
348 | |
349 | |         return True
    | |___________________^
    |
help: Replace with `return not len(set(lengths)) > 1`

F821 Undefined name `os`
   --> tests/utils.py:361:34
    |
359 |         # Save original values
360 |         for key, value in env_vars.items():
361 |             original_vars[key] = os.environ.get(key)
    |                                  ^^
362 |             os.environ[key] = value
    |

F821 Undefined name `os`
   --> tests/utils.py:362:13
    |
360 |         for key, value in env_vars.items():
361 |             original_vars[key] = os.environ.get(key)
362 |             os.environ[key] = value
    |             ^^
363 |
364 |         yield
    |

F821 Undefined name `os`
   --> tests/utils.py:370:17
    |
368 |         for key, value in original_vars.items():
369 |             if value is None:
370 |                 os.environ.pop(key, None)
    |                 ^^
371 |             else:
372 |                 os.environ[key] = value
    |

F821 Undefined name `os`
   --> tests/utils.py:372:17
    |
370 |                 os.environ.pop(key, None)
371 |             else:
372 |                 os.environ[key] = value
    |                 ^^
    |

PTH123 `open()` should be replaced by `Path.open()`
   --> tests/utils.py:424:10
    |
422 |         raise FileNotFoundError(f"Test data file not found: {file_path}")
423 |
424 |     with open(file_path, "r") as f:
    |          ^^^^
425 |         return json.load(f)
    |

UP015 [*] Unnecessary mode argument
   --> tests/utils.py:424:26
    |
422 |         raise FileNotFoundError(f"Test data file not found: {file_path}")
423 |
424 |     with open(file_path, "r") as f:
    |                          ^^^
425 |         return json.load(f)
    |
help: Remove mode argument

PTH123 `open()` should be replaced by `Path.open()`
   --> tests/utils.py:434:10
    |
433 |     file_path = test_data_dir / filename
434 |     with open(file_path, "w") as f:
    |          ^^^^
435 |         json.dump(data, f, indent=2)
    |

RUF022 [*] `__all__` is not sorted
   --> tests/utils.py:477:11
    |
476 |   # Export commonly used utilities
477 |   __all__ = [
    |  ___________^
478 | |     "TestDataGenerator",
479 | |     "MockFactory",
480 | |     "PerformanceMonitor",
481 | |     "AsyncTestHelpers",
482 | |     "TestValidators",
483 | |     "temp_env_vars",
484 | |     "mock_external_services",
485 | |     "create_test_file",
486 | |     "load_test_data",
487 | |     "save_test_data",
488 | |     "generate_random_string",
489 | |     "generate_random_email",
490 | |     "generate_random_url",
491 | |     "measure_execution_time",
492 | |     "measure_async_execution_time",
493 | | ]
    | |_^
    |
help: Apply an isort-style sorting to `__all__`

Found 1020 errors.
[*] 184 fixable with the `--fix` option (203 hidden fixes can be enabled with the `--unsafe-fixes` option).
```

## mypy (types)

```
mypy: can't read file 'ISA_SuperApp/src': No such file or directory
```

## pytest (determinism snapshot)

```
ERROR: file or directory not found: tests/unit/test_snapshot_canonical_sample.py


no tests ran in 0.00s
```

## bandit (security)

```

```

## pip-audit (deps)

```
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
WARNING:cachecontrol.controller:Cache entry deserialization failed, entry ignored
No known vulnerabilities found
Name         Skip Reason
------------ ---------------------------------------------------------------------------
isa-superapp Dependency not found on PyPI and could not be audited: isa-superapp (0.1.0)
```

## docs-ref-lint

```
wrote /Users/frisowempe/ISA_D/docs/audit/docs_ref_report.md
```

## coherence-audit

```
coherence audit artifacts written:
 - /Users/frisowempe/ISA_D/coherence_graph.json
 - /Users/frisowempe/ISA_D/orphans_and_dead_ends.md
 - /Users/frisowempe/ISA_D/TERMS.md
 - /Users/frisowempe/ISA_D/traceability_matrix.csv
 - /Users/frisowempe/ISA_D/COHERENCE_SCORECARD.md
 - /Users/frisowempe/ISA_D/contradiction_report.md
```

## coherence-scorecard

```
# Coherence Scorecard

- Reference Density: 3.76 (score 100)
- Orphan Ratio: 0.94 (score 6)
- Contradiction Count: 0 (score 100)
- Clustering Coefficient (approx): n/a (score 70)
- Coherence Index: 69

Note: Initial baseline. Improve by adding cross-links and trimming orphans where appropriate.
```
