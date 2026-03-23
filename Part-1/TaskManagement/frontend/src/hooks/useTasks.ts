import { useState, useCallback } from "react";
import { apiClient } from "../lib/api";
import type { Task } from "../lib/api";

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.getTasks();
      setTasks(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to fetch tasks";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createTask = useCallback(async (title: string, description: string) => {
    try {
      setError(null);
      const newTask = await apiClient.createTask(title, description);
      setTasks((prev) => [newTask, ...prev]);
      return newTask;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to create task";
      setError(message);
      throw err;
    }
  }, []);

  const updateTask = useCallback(async (id: string, task: Partial<Task>) => {
    try {
      setError(null);
      const updated = await apiClient.updateTask(id, task);
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
      return updated;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to update task";
      setError(message);
      throw err;
    }
  }, []);

  const deleteTask = useCallback(async (id: string) => {
    try {
      setError(null);
      await apiClient.deleteTask(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to delete task";
      setError(message);
      throw err;
    }
  }, []);

  return {
    tasks,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
  };
}
