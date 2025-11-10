import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';

// Cleanup after each test case
afterEach(() => {
  cleanup();
});

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

// Reset localStorage mocks before each test
beforeEach(() => {
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
});

// Mock PixiJS
vi.mock('pixi.js', () => ({
  Application: vi.fn(() => ({
    init: vi.fn(),
    stage: {
      addChild: vi.fn(),
    },
    renderer: {
      resize: vi.fn(),
    },
    canvas: document.createElement('canvas'),
    destroy: vi.fn(),
  })),
  Container: vi.fn(() => ({
    addChild: vi.fn(),
  })),
  Graphics: vi.fn(() => ({
    rect: vi.fn().mockReturnThis(),
    fill: vi.fn().mockReturnThis(),
  })),
  Text: vi.fn(() => ({
    anchor: { set: vi.fn() },
  })),
}));
