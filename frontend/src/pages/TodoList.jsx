import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getAllTodos, updateTodoCompletion, deleteTodo } from '../services/todoService';
import { TodoItem } from '../components/todos/TodoItem';
import { CreateTodoForm } from '../components/todos/CreateTodoForm';
import { LogoutButton } from '../components/auth/LogoutButton';
import './TodoList.css';

export function TodoList() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const fetchTodos = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getAllTodos();
      setTodos(data);
    } catch (err) {
      console.error('Failed to fetch todos:', err);
      setError('Failed to load your to-do items. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const handleTodoCreated = (newTodo) => {
    setTodos(prevTodos => [newTodo, ...prevTodos]);
  };

  const handleToggleComplete = async (id, currentStatus) => {
    setTodos(prevTodos =>
      prevTodos.map(todo =>
        todo.id === id ? { ...todo, completed: !currentStatus } : todo
      )
    );

    try {
      await updateTodoCompletion(id, !currentStatus);
    } catch (err) {
      setTodos(prevTodos =>
        prevTodos.map(todo =>
          todo.id === id ? { ...todo, completed: currentStatus } : todo
        )
      );
      setError('Failed to update todo. Please try again.');
      console.error('Failed to toggle todo:', err);
    }
  };

  const handleDelete = async (id) => {
    const todoToDelete = todos.find(todo => todo.id === id);
    setTodos(prevTodos => prevTodos.filter(todo => todo.id !== id));

    try {
      await deleteTodo(id);
    } catch (err) {
      if (todoToDelete) {
        setTodos(prevTodos => {
          const newTodos = [...prevTodos];
          const originalIndex = todos.findIndex(t => t.id === id);
          newTodos.splice(originalIndex, 0, todoToDelete);
          return newTodos;
        });
      }
      setError('Failed to delete todo. Please try again.');
      console.error('Failed to delete todo:', err);
      throw err;
    }
  };

  const clearError = () => setError('');

  const completedCount = todos.filter(todo => todo.completed).length;
  const totalCount = todos.length;

  return (
    <div className="todo-list-page">
      <header className="page-header">
        <div className="header-content">
          <h1>My To-Do List</h1>
          <div className="user-info">
            <span className="welcome-message">{user?.username}</span>
            <LogoutButton />
          </div>
        </div>
        <nav className="header-nav">
          <Link to="/" className="nav-link">← Home</Link>
        </nav>
      </header>

      <main className="page-content">
        <CreateTodoForm onTodoCreated={handleTodoCreated} />

        {error && (
          <div className="error-banner" role="alert">
            <span>{error}</span>
            <button onClick={clearError} className="dismiss-btn" aria-label="Dismiss error">
              ×
            </button>
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading your to-dos...</p>
          </div>
        ) : todos.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📝</div>
            <h2>No to-dos yet</h2>
            <p>Add your first to-do item above to get started!</p>
          </div>
        ) : (
          <>
            <div className="todo-stats">
              <span className="stats-text">
                {completedCount} of {totalCount} completed
              </span>
              {totalCount > 0 && (
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${(completedCount / totalCount) * 100}%` }}
                  ></div>
                </div>
              )}
            </div>

            <ul className="todo-list" aria-label="To-do items">
              {todos.map(todo => (
                <TodoItem
                  key={todo.id}
                  todo={todo}
                  onToggleComplete={handleToggleComplete}
                  onDelete={handleDelete}
                />
              ))}
            </ul>
          </>
        )}
      </main>
    </div>
  );
}

export default TodoList;
