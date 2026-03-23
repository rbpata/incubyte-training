import { useState } from "react";
import type { Task } from "../lib/api";
import { TaskCard } from "./TaskCard";

interface TaskListProps {
  tasks: Task[];
  onToggle: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
}

export function TaskList({ tasks, onToggle, onDelete }: TaskListProps) {
  const [filterBy, setFilterBy] = useState<"all" | "active" | "completed">(
    "all",
  );

  const filtered = tasks.filter((task) => {
    if (filterBy === "active") return !task.completed;
    if (filterBy === "completed") return task.completed;
    return true;
  });

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {(["all", "active", "completed"] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilterBy(status)}
            className={`px-4 py-2 rounded capitalize transition ${
              filterBy === status
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:border-gray-400"
            }`}
          >
            {status}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <p>No tasks yet. Create one to get started!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggle={onToggle}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
