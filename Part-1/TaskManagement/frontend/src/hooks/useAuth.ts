import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../lib/api";
import type { User } from "../lib/api";
import { saveToken, clearToken, getToken } from "../lib/auth";

export function useAuth() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (getToken()) {
      fetchCurrentUser();
    }
  }, []);

  const fetchCurrentUser = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getCurrentUser();
      setUser(data);
    } catch (err) {
      clearToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signup = useCallback(
    async (username: string, email: string, password: string) => {
      try {
        setIsLoading(true);
        setError(null);
        await apiClient.signup(username, email, password);
        navigate("/login");
      } catch (err) {
        const message = err instanceof Error ? err.message : "Signup failed";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [navigate],
  );

  const login = useCallback(
    async (username: string, password: string) => {
      try {
        setIsLoading(true);
        setError(null);
        const token = await apiClient.login(username, password);
        saveToken(token.access_token);
        await fetchCurrentUser();
        navigate("/tasks");
      } catch (err) {
        const message = err instanceof Error ? err.message : "Login failed";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [navigate, fetchCurrentUser],
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    navigate("/login");
  }, [navigate]);

  return {
    user,
    isLoading,
    error,
    signup,
    login,
    logout,
    isAuthenticated: !!user,
  };
}
