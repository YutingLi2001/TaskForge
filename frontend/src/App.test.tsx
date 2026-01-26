import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import App from './App';

describe('App', () => {
  it('routes to login by default', async () => {
    render(<App />);

    expect(
      await screen.findByRole('heading', { name: 'Log In' })
    ).toBeInTheDocument();
  });
});
