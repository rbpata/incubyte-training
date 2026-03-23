import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";
import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../lib/api";
import type { User } from "../lib/api";
import { saveToken, clearToken, getToken } from "../lib/auth";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  signup: (username: string, email: string, password: string) => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initAuth = async () => {
      if (getToken()) {
        try {
          const data = await apiClient.getCurrentUser();
          setUser(data);
        } catch (err) {
          clearToken();
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
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
        const userData = await apiClient.getCurrentUser();
        setUser(userData);
        navigate("/tasks");
      } catch (err) {
        const message = err instanceof Error ? err.message : "Login failed";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [navigate],
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    navigate("/login");
  }, [navigate]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        error,
        isAuthenticated: !!user,
        signup,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
}
