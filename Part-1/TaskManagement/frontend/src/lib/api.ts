import axios from "axios";
import type { AxiosInstance, AxiosError } from "axios";
import { getToken } from "./auth";

const API_BASE_URL = "http://localhost:8000";

export interface User {
  id: string;
  username: string;
  email: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

function removeUndefinedValues<T extends Record<string, unknown>>(
  obj: T,
): Partial<T> {
  return Object.fromEntries(
    Object.entries(obj).filter(([, value]) => value !== undefined),
  ) as Partial<T>;
}

class ApiClient {
  private httpClient: AxiosInstance;

  constructor(baseURL: string) {
    this.httpClient = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.httpClient.interceptors.request.use((config) => {
      const token = getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.httpClient.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const message = this.extractErrorMessage(error);
        throw new Error(message);
      },
    );
  }

  private extractErrorMessage(error: AxiosError): string {
    if (error.response?.data) {
      const data = error.response.data as Record<string, unknown>;
      if (typeof data.detail === "string") {
        return data.detail;
      }
    }

    if (error.message) {
      return error.message;
    }

    return "An unexpected error occurred";
  }

  async signup(
    username: string,
    email: string,
    password: string,
  ): Promise<User> {
    const response = await this.httpClient.post<User>("/users", {
      username,
      email,
      password,
    });
    return response.data;
  }

  async login(username: string, password: string): Promise<Token> {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    const response = await this.httpClient.post<Token>("/token", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.httpClient.get<User>("/users/me");
    return response.data;
  }

  async getTasks(
    filterBy?: string,
    order?: string,
    limit?: number,
    offset?: number,
  ): Promise<Task[]> {
    const params = removeUndefinedValues({
      filter_by: filterBy,
      order: order || "asc",
      limit,
      offset,
    });

    const response = await this.httpClient.get<Task[]>("/tasks", {
      params,
    });
    return response.data;
  }

  async createTask(title: string, description: string): Promise<Task> {
    const response = await this.httpClient.post<Task>("/tasks", {
      title,
      description,
    });
    return response.data;
  }

  async updateTask(id: string, task: Partial<Task>): Promise<Task> {
    const response = await this.httpClient.put<Task>(`/tasks/${id}`, task);
    return response.data;
  }

  async deleteTask(id: string): Promise<Task> {
    const response = await this.httpClient.delete<Task>(`/tasks/${id}`);
    return response.data;
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
