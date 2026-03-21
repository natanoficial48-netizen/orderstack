cat > app/models/base.py << 'EOF'
"""
Base compartilhada para todos os modelos do sistema.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
EOF