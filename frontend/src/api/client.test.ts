import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { authApi } from './client';

describe('authApi', () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    localStorage.clear();
    fetchMock.mockReset();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('includes Authorization header when token is present', async () => {
    localStorage.setItem('token', 'token-123');
    fetchMock.mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        data: {
          access_token: 'access',
          token_type: 'bearer',
          user: { id: 1, email: 'user@example.com', created_at: '2026-01-19T00:00:00Z' },
        },
      }),
    });

    await authApi.login({ email: 'user@example.com', password: 'secret123' });

    const [, options] = fetchMock.mock.calls[0];
    const headers = options?.headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer token-123');
  });
});
