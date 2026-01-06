import api from './api';

/**
 * Get all todos for the authenticated user.
 * Returns todos in reverse chronological order (newest first).
 */
export const getAllTodos = async () => {
  const response = await api.get('/api/todos');
  return response.data;
};

/**
 * Create a new todo item.
 * @param {string} text - Todo text (1-500 characters)
 */
export const createTodo = async (text) => {
  const response = await api.post('/api/todos', { text });
  return response.data;
};

/**
 * Update a todo's completion status.
 * @param {number} id - Todo ID
 * @param {boolean} completed - New completion status
 */
export const updateTodoCompletion = async (id, completed) => {
  const response = await api.patch(`/api/todos/${id}`, { completed });
  return response.data;
};

/**
 * Delete a todo item permanently.
 * @param {number} id - Todo ID
 */
export const deleteTodo = async (id) => {
  await api.delete(`/api/todos/${id}`);
};
