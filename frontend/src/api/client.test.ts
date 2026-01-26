import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  ApiRequestError,
  api,
  authApi,
  projectsApi,
  tasksApi,
} from './client';

const mockFetch = vi.fn();

describe('tasksApi', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('list calls api.get with project tasks path', async () => {
    const mockGet = vi.spyOn(api, 'get').mockResolvedValue({ data: [] });

    await tasksApi.list(5);

    expect(mockGet).toHaveBeenCalledWith('/projects/5/tasks');
  });

  it('create calls api.post with project tasks path and data', async () => {
    const payload = { title: 'New Task' };
    const mockPost = vi.spyOn(api, 'post').mockResolvedValue({ data: { ...payload } });

    await tasksApi.create(7, payload);

    expect(mockPost).toHaveBeenCalledWith('/projects/7/tasks', payload);
  });

  it('delete calls api.delete with project task path', async () => {
    const mockDelete = vi.spyOn(api, 'delete').mockResolvedValue({ data: {} });

    await tasksApi.delete(9, 12);

    expect(mockDelete).toHaveBeenCalledWith('/projects/9/tasks/12');
  });
});

describe('api request', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', mockFetch);
    localStorage.clear();
  });

  afterEach(() => {
    mockFetch.mockReset();
    vi.unstubAllGlobals();
  });

  it('adds auth header and sends JSON body', async () => {
    localStorage.setItem('token', 'token-123');
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ data: { ok: true } }),
    });

    await api.post('/auth/login', { email: 'user@example.com' });

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          Authorization: 'Bearer token-123',
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('throws ApiRequestError with detail from response', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Invalid credentials' }),
    });

    await expect(api.get('/auth/me')).rejects.toMatchObject({
      name: 'ApiRequestError',
      status: 401,
      detail: 'Invalid credentials',
    });
  });

  it('handles non-JSON error responses', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error('bad json');
      },
    });

    await expect(api.get('/auth/me')).rejects.toBeInstanceOf(ApiRequestError);
  });
});

describe('authApi and projectsApi', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('authApi.login calls api.post with payload', async () => {
    const mockPost = vi.spyOn(api, 'post').mockResolvedValue({ data: {} });
    const payload = { email: 'user@example.com', password: 'secret' };

    await authApi.login(payload);

    expect(mockPost).toHaveBeenCalledWith('/auth/login', payload);
  });

  it('projectsApi.update calls api.put with path and data', async () => {
    const mockPut = vi.spyOn(api, 'put').mockResolvedValue({ data: {} });
    const payload = { name: 'Updated' };

    await projectsApi.update(4, payload);

    expect(mockPut).toHaveBeenCalledWith('/projects/4', payload);
  });
});
