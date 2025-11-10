# AICraft Frontend Tests

## Quick Start

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui

# Watch mode
npm test -- --watch
```

## Test Structure

```
src/
├── __tests__/
│   ├── setup.js          # Test configuration
│   ├── test-utils.jsx    # Reusable test utilities
│   └── README.md         # This file
├── __mocks__/
│   └── api.js            # Mock API implementation
└── components/
    └── __tests__/        # Component tests
        ├── PokemonButton.test.jsx
        ├── ThemeToggle.test.jsx
        ├── AgentCard.test.jsx
        ├── AgentCreation.test.jsx
        ├── WorldCreation.test.jsx
        └── App.test.jsx
```

## Test Coverage

**Overall: 96.47%**
- Statements: 96.47%
- Branches: 90.36%
- Functions: 93.1%
- Lines: 96.25%

## Writing Tests

### Import Test Utilities
```javascript
import { render, screen, waitFor, mockAgents } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
```

### Mock API Calls
```javascript
import * as api from '../../api'

vi.mock('../../api', () => ({
  api: {
    createAgentStream: vi.fn()
  }
}))
```

### Basic Test Pattern
```javascript
it('renders component correctly', () => {
  render(<MyComponent />)
  expect(screen.getByText('Expected Text')).toBeInTheDocument()
})
```

### Testing User Interactions
```javascript
it('handles button click', async () => {
  const user = userEvent.setup()
  render(<MyComponent />)

  const button = screen.getByRole('button', { name: /click me/i })
  await user.click(button)

  expect(screen.getByText('Clicked!')).toBeInTheDocument()
})
```

### Testing Async Operations
```javascript
it('loads data', async () => {
  render(<MyComponent />)

  await waitFor(() => {
    expect(screen.getByText('Loaded Data')).toBeInTheDocument()
  })
})
```

## Available Test Fixtures

### Mock Agents
```javascript
import { mockAgents } from '../../__tests__/test-utils'

mockAgents.basic           // Basic agent with no avatar
mockAgents.withHttpAvatar  // Agent with HTTP avatar URL
mockAgents.withDataUriAvatar // Agent with data URI avatar
mockAgents.manyTraits      // Agent with 12 personality traits
```

### Mock Worlds
```javascript
import { mockWorlds } from '../../__tests__/test-utils'

mockWorlds.basic  // Basic 10x10 world
```

## Common Patterns

### Testing Forms
```javascript
const textarea = screen.getByPlaceholderText(/enter text/i)
await user.type(textarea, 'Test input')

const button = screen.getByRole('button', { name: /submit/i })
await user.click(button)
```

### Testing Error States
```javascript
api.createAgent.mockRejectedValue(new Error('API Error'))

// Trigger the error...

await waitFor(() => {
  expect(screen.getByText(/error/i)).toBeInTheDocument()
})
```

### Testing Loading States
```javascript
api.createAgent.mockImplementation(() => new Promise(() => {})) // Never resolves

// Trigger loading...

expect(screen.getByText(/loading/i)).toBeInTheDocument()
```

## Tips

1. **Use `screen.debug()`** to see the current DOM when debugging
2. **Prefer semantic queries**: Use `getByRole`, `getByLabelText`, `getByText` over `getByTestId`
3. **Test behavior, not implementation**: Focus on what users see and do
4. **Mock external dependencies**: Use vi.mock() for API calls and external libraries
5. **Clean up after tests**: The setup file handles cleanup automatically

## Troubleshooting

### Test Timeout
If a test times out, check:
- Are you waiting for async operations with `waitFor()`?
- Is your mock returning a resolved promise?
- Do you have infinite loops or recursive calls?

### Element Not Found
- Use `screen.debug()` to see what's rendered
- Check if the element is conditional (requires state change)
- Verify your query matches the actual text/role

### Mock Not Working
- Ensure `vi.mock()` is called before importing the component
- Check that you're mocking the correct import path
- Verify the mock is properly configured (return values, implementations)

## Coverage Reports

Coverage reports are generated in `/coverage/`:
- Open `coverage/index.html` in a browser for interactive view
- Red = not covered
- Yellow = partially covered (branches)
- Green = fully covered

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [User Event Library](https://testing-library.com/docs/user-event/intro)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
