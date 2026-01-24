import { afterEach, describe, expect, it, vi } from 'vitest';

import { api, tasksApi } from './client';

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
