import { useEffect, useState } from "react";
import { useAuthContext } from "../contexts/AuthContext";
import { useTasks } from "../hooks/useTasks";
import { TaskForm } from "../components/TaskForm";
import { TaskList } from "../components/TaskList";

export function TasksPage() {
  const { user, logout } = useAuthContext();
  const {
    tasks,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
  } = useTasks();
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleCreateTask = async (title: string, description: string) => {
    setIsCreating(true);
    try {
      await createTask(title, description);
    } finally {
      setIsCreating(false);
    }
  };

  const handleToggleTask = async (id: string, completed: boolean) => {
    await updateTask(id, { completed });
  };

  const handleDeleteTask = async (id: string) => {
    if (confirm("Are you sure you want to delete this task?")) {
      await deleteTask(id);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
            {user && <p className="text-gray-600">Welcome, {user.username}</p>}
          </div>
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8 space-y-8">
        {/* Task Form */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Create a New Task
          </h2>
          <TaskForm onSubmit={handleCreateTask} isLoading={isCreating} />
        </section>

        {/* Tasks List */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Your Tasks
          </h2>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}
          {isLoading ? (
            <div className="text-center py-8">
              <p className="text-gray-500">Loading tasks...</p>
            </div>
          ) : (
            <TaskList
              tasks={tasks}
              onToggle={handleToggleTask}
              onDelete={handleDeleteTask}
            />
          )}
        </section>
      </main>
    </div>
  );
}
