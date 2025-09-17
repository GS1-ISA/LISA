#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <NAME>"
    exit 1
fi

NAME=$1

COMPONENT_DIR="frontend/src/components/$NAME"

mkdir -p "$COMPONENT_DIR"

# Create index.tsx
cat > "$COMPONENT_DIR/index.tsx" << EOF
import React from 'react';

const $NAME = () => {
    return <div>$NAME Component</div>;
};

export default $NAME;
EOF

# Create test stub
cat > "$COMPONENT_DIR/$NAME.test.tsx" << EOF
import React from 'react';
import { render, screen } from '@testing-library/react';
import $NAME from './index';

describe('$NAME', () => {
    it('renders the component', () => {
        render(<$NAME />);
        expect(screen.getByText('$NAME Component')).toBeInTheDocument();
    });
});
EOF

# Add to docs/project-structure.md
echo "- frontend/src/components/$NAME/" >> docs/project-structure.md

# Git add
git add "$COMPONENT_DIR/index.tsx" "$COMPONENT_DIR/$NAME.test.tsx"