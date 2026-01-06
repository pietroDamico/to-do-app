import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from './api';
import { getAllTodos, createTodo, updateTodoCompletion, deleteTodo } from './todoService';

vi.mock('./api');

describe('todoService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getAllTodos', () => {
    it('should fetch all todos', async () => {
      const mockTodos = [
        { id: 1, text: 'Test todo 1', completed: false },
        { id: 2, text: 'Test todo 2', completed: true },
      ];
      api.get.mockResolvedValue({ data: mockTodos });

      const result = await getAllTodos();

      expect(api.get).toHaveBeenCalledWith('/api/todos');
      expect(result).toEqual(mockTodos);
    });

    it('should throw error on API failure', async () => {
      const error = new Error('Network error');
      api.get.mockRejectedValue(error);

      await expect(getAllTodos()).rejects.toThrow('Network error');
    });
  });

  describe('createTodo', () => {
    it('should create a new todo', async () => {
      const mockTodo = { id: 1, text: 'New todo', completed: false };
      api.post.mockResolvedValue({ data: mockTodo });

      const result = await createTodo('New todo');

      expect(api.post).toHaveBeenCalledWith('/api/todos', { text: 'New todo' });
      expect(result).toEqual(mockTodo);
    });

    it('should throw error on API failure', async () => {
      const error = new Error('Failed to create');
      api.post.mockRejectedValue(error);

      await expect(createTodo('Test')).rejects.toThrow('Failed to create');
    });
  });

  describe('updateTodoCompletion', () => {
    it('should update todo completion status to true', async () => {
      const mockTodo = { id: 1, text: 'Test', completed: true };
      api.patch.mockResolvedValue({ data: mockTodo });

      const result = await updateTodoCompletion(1, true);

      expect(api.patch).toHaveBeenCalledWith('/api/todos/1', { completed: true });
      expect(result).toEqual(mockTodo);
    });

    it('should update todo completion status to false', async () => {
      const mockTodo = { id: 1, text: 'Test', completed: false };
      api.patch.mockResolvedValue({ data: mockTodo });

      const result = await updateTodoCompletion(1, false);

      expect(api.patch).toHaveBeenCalledWith('/api/todos/1', { completed: false });
      expect(result).toEqual(mockTodo);
    });

    it('should throw error on API failure', async () => {
      const error = new Error('Failed to update');
      api.patch.mockRejectedValue(error);

      await expect(updateTodoCompletion(1, true)).rejects.toThrow('Failed to update');
    });
  });

  describe('deleteTodo', () => {
    it('should delete a todo', async () => {
      api.delete.mockResolvedValue({});

      await deleteTodo(1);

      expect(api.delete).toHaveBeenCalledWith('/api/todos/1');
    });

    it('should throw error on API failure', async () => {
      const error = new Error('Failed to delete');
      api.delete.mockRejectedValue(error);

      await expect(deleteTodo(1)).rejects.toThrow('Failed to delete');
    });
  });
});
