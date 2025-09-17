import React from 'react';
import { render, screen } from '@testing-library/react';
import Demo from './index';

describe('Demo', () => {
    it('renders the component', () => {
        render(<Demo />);
        expect(screen.getByText('Demo Component')).toBeInTheDocument();
    });
});
