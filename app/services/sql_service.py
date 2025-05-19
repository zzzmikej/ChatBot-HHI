import sqlglot
import os
import re
import glob
from typing import List, Tuple, Optional, Any

_db_schema_cache = None