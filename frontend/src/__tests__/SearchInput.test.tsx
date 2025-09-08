import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Mock the SearchInput component
const SearchInput: React.FC<{
  onSearch: (ticker: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}> = ({ onSearch, isLoading = false, placeholder = "Enter NSE ticker symbol (e.g., RELIANCE)" }) => {
  const [value, setValue] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !isLoading) {
      onSearch(value.trim().toUpperCase());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md">
      <div className="relative">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          disabled={isLoading}
          className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        <button
          type="submit"
          disabled={isLoading || !value.trim()}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-1.5 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </form>
  );
};

describe('SearchInput Component', () => {
  const mockOnSearch = jest.fn();

  beforeEach(() => {
    mockOnSearch.mockClear();
  });

  test('renders with placeholder text', () => {
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const input = screen.getByPlaceholderText(/enter nse ticker symbol/i);
    expect(input).toBeInTheDocument();
  });

  test('renders with custom placeholder', () => {
    const customPlaceholder = "Custom placeholder";
    render(<SearchInput onSearch={mockOnSearch} placeholder={customPlaceholder} />);
    
    const input = screen.getByPlaceholderText(customPlaceholder);
    expect(input).toBeInTheDocument();
  });

  test('calls onSearch when form is submitted', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /search/i });
    
    await user.type(input, 'RELIANCE');
    await user.click(button);
    
    expect(mockOnSearch).toHaveBeenCalledWith('RELIANCE');
  });

  test('calls onSearch when Enter key is pressed', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const input = screen.getByRole('textbox');
    
    await user.type(input, 'TCS');
    await user.keyboard('{Enter}');
    
    expect(mockOnSearch).toHaveBeenCalledWith('TCS');
  });

  test('trims whitespace and converts to uppercase', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /search/i });
    
    await user.type(input, '  reliance  ');
    await user.click(button);
    
    expect(mockOnSearch).toHaveBeenCalledWith('RELIANCE');
  });

  test('does not call onSearch with empty input', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const button = screen.getByRole('button', { name: /search/i });
    
    await user.click(button);
    
    expect(mockOnSearch).not.toHaveBeenCalled();
  });

  test('does not call onSearch with only whitespace', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /search/i });
    
    await user.type(input, '   ');
    await user.click(button);
    
    expect(mockOnSearch).not.toHaveBeenCalled();
  });

  test('disables input and button when loading', () => {
    render(<SearchInput onSearch={mockOnSearch} isLoading={true} />);
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /searching/i });
    
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });

  test('shows loading text when loading', () => {
    render(<SearchInput onSearch={mockOnSearch} isLoading={true} />);
    
    expect(screen.getByText('Searching...')).toBeInTheDocument();
  });

  test('disables button when input is empty', () => {
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const button = screen.getByRole('button', { name: /search/i });
    
    expect(button).toBeDisabled();
  });

  test('enables button when input has value', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /search/i });
    
    expect(button).toBeDisabled();
    
    await user.type(input, 'INFY');
    
    expect(button).not.toBeDisabled();
  });

  test('updates input value as user types', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={mockOnSearch} />);
    
    const input = screen.getByRole('textbox') as HTMLInputElement;
    
    await user.type(input, 'HDFC');
    
    expect(input.value).toBe('HDFC');
  });

  test('prevents submission when loading', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={mockOnSearch} isLoading={true} />);
    
    // Try to submit by pressing Enter
    const input = screen.getByRole('textbox');
    await user.type(input, 'TEST');
    await user.keyboard('{Enter}');
    
    expect(mockOnSearch).not.toHaveBeenCalled();
  });
});