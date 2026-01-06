import { useState } from 'react';
import './TodoItem.css';

export function TodoItem({ todo, onToggleComplete, onDelete }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const handleToggle = async () => {
    if (isToggling) return;
    setIsToggling(true);
    try {
      await onToggleComplete(todo.id, todo.completed);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    if (isDeleting) return;
    
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }
    
    setIsDeleting(true);
    try {
      await onDelete(todo.id);
    } catch (error) {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <li className={`todo-item ${todo.completed ? 'completed' : ''} ${isDeleting ? 'deleting' : ''}`}>
      <label className="todo-checkbox-label">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={handleToggle}
          disabled={isToggling || isDeleting}
          className="todo-checkbox"
          aria-label={`Mark "${todo.text}" as ${todo.completed ? 'incomplete' : 'complete'}`}
        />
        <span className="todo-checkmark"></span>
      </label>
      
      <div className="todo-content">
        <span className="todo-text">{todo.text}</span>
        <span className="todo-date">{formatDate(todo.created_at)}</span>
      </div>
      
      <button
        onClick={handleDelete}
        disabled={isDeleting}
        className="todo-delete-btn"
        aria-label={`Delete "${todo.text}"`}
        type="button"
      >
        {isDeleting ? 'Deleting...' : 'Delete'}
      </button>
    </li>
  );
}

export default TodoItem;
