import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => {
  const renderMock = vi.fn();
  const createRootMock = vi.fn(() => ({ render: renderMock }));
  return { renderMock, createRootMock };
});

vi.mock('react-dom/client', () => ({
  createRoot: mocks.createRootMock,
}));

describe('main', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="root"></div>';
    vi.resetModules();
    mocks.renderMock.mockClear();
    mocks.createRootMock.mockClear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mounts the app into the root element', async () => {
    await import('./main');

    expect(mocks.createRootMock).toHaveBeenCalledWith(
      document.getElementById('root')
    );
    expect(mocks.renderMock).toHaveBeenCalledTimes(1);
  });
});
