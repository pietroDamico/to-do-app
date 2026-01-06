import { useState } from 'react';
import { createTodo } from '../../services/todoService';
import './CreateTodoForm.css';

export function CreateTodoForm({ onTodoCreated }) {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const validateText = (value) => {
    if (!value.trim()) {
      return 'Todo text cannot be empty';
    }
    if (value.length > 500) {
      return 'Todo text must be 500 characters or less';
    }
    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateText(text);
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setLoading(true);
      setError('');
      const newTodo = await createTodo(text.trim());
      setText('');
      onTodoCreated(newTodo);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to create todo';
      setError(typeof errorMessage === 'string' ? errorMessage : 'Failed to create todo');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e) => {
    setText(e.target.value);
    if (error) {
      setError('');
    }
  };

  const remainingChars = 500 - text.length;

  return (
    <form className="create-todo-form" onSubmit={handleSubmit} noValidate>
      <div className="form-group">
        <label htmlFor="todo-text" className="form-label">
          Add a new to-do
        </label>
        <div className="input-wrapper">
          <input
            id="todo-text"
            type="text"
            value={text}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="What needs to be done?"
            maxLength={500}
            disabled={loading}
            className={`todo-input ${error ? 'error' : ''}`}
            aria-describedby={error ? 'todo-error' : undefined}
            aria-invalid={!!error}
          />
          <span className={`char-count ${remainingChars < 50 ? 'warning' : ''}`}>
            {remainingChars}
          </span>
        </div>
      </div>
      
      {error && (
        <div id="todo-error" className="error-message" role="alert">
          {error}
        </div>
      )}
      
      <button
        type="submit"
        disabled={loading || !text.trim()}
        className="submit-btn"
      >
        {loading ? 'Adding...' : 'Add Todo'}
      </button>
    </form>
  );
}

export default CreateTodoForm;
