import type { Task } from "../lib/api";

interface TaskCardProps {
  task: Task;
  onToggle: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
}

export function TaskCard({ task, onToggle, onDelete }: TaskCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4 flex items-start gap-4">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={(e) => onToggle(task.id, e.target.checked)}
        className="mt-1 w-5 h-5 text-blue-600 rounded cursor-pointer"
      />

      <div className="flex-1 min-w-0">
        <h3
          className={`font-semibold text-lg break-words ${
            task.completed ? "line-through text-gray-400" : "text-gray-900"
          }`}
        >
          {task.title}
        </h3>
        {task.description && (
          <p className="text-gray-600 mt-1 text-sm break-words">
            {task.description}
          </p>
        )}
        <p className="text-xs text-gray-400 mt-2">
          {new Date(task.created_at).toLocaleDateString()}
        </p>
      </div>

      <button
        onClick={() => onDelete(task.id)}
        className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition text-sm flex-shrink-0"
      >
        Delete
      </button>
    </div>
  );
}
